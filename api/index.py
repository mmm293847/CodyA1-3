import json
import os

from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

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

다음 자기소개서를 분석해라.

[지원 직무]
{job}

[자기소개서 문항]
{question}

[자기소개서]
{essay}

다음 기준으로 평가해라.

문장 표현
구조
구체성
직무 적합성
설득력

각 점수는 0~100 사이의 정수로 작성한다.

그리고 다음 정보를 제공한다.

종합 점수
각 항목별 점수
잘된 점 3개
개선할 점 3개
추천 키워드 4개
채용 담당자 관점의 한줄 평가

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

    # Gemini가 ```json 형태로 반환할 경우 제거
    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # JSON 부분 추출
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise Exception(
            "AI가 올바른 JSON 결과를 반환하지 않았습니다."
        )

    text = text[start:end + 1]

    return json.loads(text)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "요청 데이터가 없습니다."
            }), 400

        job = data.get("job", "").strip()
        question = data.get("question", "").strip()
        essay = data.get("essay", "").strip()

        if not job:
            return jsonify({
                "error": "지원 직무를 입력해주세요."
            }), 400

        if not question:
            return jsonify({
                "error": "자기소개서 문항을 입력해주세요."
            }), 400

        if not essay:
            return jsonify({
                "error": "자기소개서를 입력해주세요."
            }), 400

        result = analyze_with_gemini(
            job,
            question,
            essay
        )

        return jsonify(result), 200

    except Exception as error:
        print("AI ERROR:", error)

        return jsonify({
            "error": "AI 분석 중 문제가 발생했습니다.",
            "detail": str(error)
        }), 500


@app.route("/api", methods=["GET"])
def api_status():
    return jsonify({
        "status": "ok",
        "message": "JASO AI API is running."
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )