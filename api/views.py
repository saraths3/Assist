import platform
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google import genai
from .serializers import FileProcessSerializer
from django.conf import settings

model_name = "gemini-3.5-flash"

@api_view(('GET',))
def info(request):
    return Response({
        'OS':platform.system(),
        'Achitecture': platform.architecture(),
        'Release': platform.release(),
        'Machine': platform.machine(),
        'python_version': platform.python_version(),
    })

from google.genai import types

@api_view(('POST',))
def file_process(request):
    serializer = FileProcessSerializer(data=request.data)
    if serializer.is_valid():
        file_path = serializer.validated_data['file_path']
        content = serializer.validated_data['content']
        flag = serializer.validated_data['flag']
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        instruction = flag.replace("_", " ") if flag else "fix"
        prompt = f"""Task: {instruction}
        
        File: {file_path}
        
        ```python
        {content}
        ```"""
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a precise code processing engine. "
                        "Return ONLY the modified code or the direct result of the task. "
                        "Do not include conversational filler, introductory text, explanations, or greetings "
                        "unless the user's task explicitly asks for an explanation."
                    ),
                )
            )
            return Response({'status': 'success', 'response': response.text}, status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            error_str = str(e)
            
            if '429' in error_str or 'resource_exhausted' in error_str:
                return Response({"error": "Rate limit exceeded. Please slow down and try again.", "details": error_str}, status=status.HTTP_400_BAD_REQUEST)
            elif '503' in error_str or 'service_unavailable' in error_str:
                return Response({"error": f"The model {model_name} is currently overloaded.", "details": error_str}, status=status.HTTP_400_BAD_REQUEST)
            elif '404' in error_str or 'not_found' in error_str:
                return Response({"error": f"The model {model_name} is unavailable.", "details": error_str}, status=status.HTTP_400_BAD_REQUEST)
            elif '401' in error_str or '403' in error_str or 'permission_denied' in error_str:
                return Response({"error": "Authentication failed. Check your GEMINI_API_KEY.", "details": error_str}, status=status.HTTP_400_BAD_REQUEST)
            elif '400' in error_str or 'invalid_argument' in error_str:
                return Response({"error": "Invalid request format.", "details": error_str}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': error_str}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)