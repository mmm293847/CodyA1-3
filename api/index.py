
import json
import os

from google import genai


def analyze_with_gemini(job, question, essay):

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise Exception(
            "GEMINI_API_KEY가 설정되지 않았습니다."
        )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
너는 채용 담당자의 관점에서 자기소개서를 분석하는 AI다.

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

    # ```json ... ``` 제거
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # JSON 앞뒤에 이상한 문자가 붙었을 경우
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise Exception(
            "AI가 올바른 JSON 결과를 반환하지 않았습니다."
        )

    text = text[start:end + 1]

    result = json.loads(text)

    return result


def handler(request):

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps({
                "error": "POST 요청만 허용됩니다."
            }, ensure_ascii=False)
        }

    try:

        data = request.get_json()

        if not data:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type":
                        "application/json; charset=utf-8"
                },
                "body": json.dumps({
                    "error": "요청 데이터가 없습니다."
                }, ensure_ascii=False)
            }

        job = data.get("job", "").strip()
        question = data.get("question", "").strip()
        essay = data.get("essay", "").strip()

        if not job:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type":
                        "application/json; charset=utf-8"
                },
                "body": json.dumps({
                    "error":
                        "지원 직무를 입력해주세요."
                }, ensure_ascii=False)
            }

        if not question:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type":
                        "application/json; charset=utf-8"
                },
                "body": json.dumps({
                    "error":
                        "자기소개서 문항을 입력해주세요."
                }, ensure_ascii=False)
            }

        if not essay:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type":
                        "application/json; charset=utf-8"
                },
                "body": json.dumps({
                    "error":
                        "자기소개서를 입력해주세요."
                }, ensure_ascii=False)
            }

        result = analyze_with_gemini(
            job,
            question,
            essay
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type":
                    "application/json; charset=utf-8"
            },
            "body": json.dumps(
                result,
                ensure_ascii=False
            )
        }

    except Exception as error:

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type":
                    "application/json; charset=utf-8"
            },
            "body": json.dumps({
                "error":
                    "AI 분석 중 문제가 발생했습니다.",
                "detail":
                    str(error)
            }, ensure_ascii=False)
        }
