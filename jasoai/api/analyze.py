import json
import os

from google import genai
from http.server import BaseHTTPRequestHandler


def analyze_with_gemini(job, question, essay):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise Exception("GEMINI_API_KEY가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
너는 채용 담당자의 관점에서 자기소개서를 분석하는 AI다.

다음 자기소개서를 분석해라.

[지원 직무]
{job}

[자기소개서 문항]
{question}

[자기소개서]
{essay}

다음 기준으로 평가해라.

1. 문장 표현
2. 구조
3. 구체성
4. 직무 적합성
5. 설득력

각 점수는 0~100 사이의 정수로 작성한다.

그리고 다음 정보를 제공한다.

- 종합 점수
- 각 항목별 점수
- 잘된 점 3개
- 개선할 점 3개
- 추천 키워드 4개
- 채용 담당자 관점의 한줄 평가

반드시 아래 JSON 구조를 지켜라.

{{
  "total_score": 0,
  "scores": {{
    "expression": 0,
    "structure": 0,
    "specificity": 0,
    "job_fit": 0,
    "persuasiveness": 0
  }},
  "strengths": [],
  "improvements": [],
  "keywords": [],
  "recruiter_comment": ""
}}

JSON 외의 설명은 작성하지 마라.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()

    # 혹시 ```json ... ``` 형태로 반환될 경우 제거
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(body)

            job = data.get("job", "").strip()
            question = data.get("question", "").strip()
            essay = data.get("essay", "").strip()

            if not job:
                self.send_error(
                    400,
                    "지원 직무를 입력해주세요."
                )
                return

            if not question:
                self.send_error(
                    400,
                    "자기소개서 문항을 입력해주세요."
                )
                return

            if not essay:
                self.send_error(
                    400,
                    "자기소개서를 입력해주세요."
                )
                return

            result = analyze_with_gemini(
                job,
                question,
                essay
            )

            response = json.dumps(
                result,
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(response))
            )

            self.end_headers()

            self.wfile.write(response)

        except Exception as error:

            response = json.dumps(
                {
                    "error": "AI 분석 중 문제가 발생했습니다.",
                    "detail": str(error)
                },
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(response))
            )

            self.end_headers()

            self.wfile.write(response)
