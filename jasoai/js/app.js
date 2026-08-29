/* ========================================
   JASO AI
   Frontend Application
======================================== */


/* ========================================
   1. DOM Elements
======================================== */

const sections = document.querySelectorAll(".page-section");
const navigationButtons = document.querySelectorAll("[data-section]");
const navLinks = document.querySelectorAll(".nav-link");

const mobileMenuButton =
  document.querySelector(".mobile-menu-button");

const nav =
  document.querySelector(".nav");

const essayInput =
  document.querySelector("#essay");

const essayCount =
  document.querySelector("#essay-count");

const jobInput =
  document.querySelector("#job");

const questionInput =
  document.querySelector("#question");

const analyzeButton =
  document.querySelector("#analyze-button");

const formMessage =
  document.querySelector("#form-message");


/* ========================================
   2. Section Navigation
======================================== */

function showSection(sectionName) {

  sections.forEach((section) => {
    section.classList.remove("active");
  });

  const targetSection =
    document.querySelector(`#${sectionName}-section`);

  if (!targetSection) {
    return;
  }

  targetSection.classList.add("active");


  navLinks.forEach((link) => {
    link.classList.remove("active");

    if (link.dataset.section === sectionName) {
      link.classList.add("active");
    }
  });


  nav.classList.remove("mobile-open");


  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });
}


/* ========================================
   3. Navigation Event
======================================== */

navigationButtons.forEach((button) => {

  button.addEventListener("click", () => {

    const sectionName =
      button.dataset.section;

    showSection(sectionName);

  });

});


/* ========================================
   4. Mobile Navigation
======================================== */

if (mobileMenuButton) {

  mobileMenuButton.addEventListener("click", () => {

    nav.classList.toggle("mobile-open");

  });

}


/* ========================================
   5. Essay Character Count
======================================== */

if (essayInput && essayCount) {

  essayInput.addEventListener("input", () => {

    const count =
      essayInput.value.length;

    essayCount.textContent =
      `${count.toLocaleString()}자`;

  });

}


/* ========================================
   6. Form Message
======================================== */

function showFormMessage(message) {

  formMessage.textContent = message;
  formMessage.classList.remove("hidden");

}


function hideFormMessage() {

  formMessage.textContent = "";
  formMessage.classList.add("hidden");

}


/* ========================================
7. API Result Normalize
======================================== */

function normalizeResult(data) {

return {
totalScore: data.total_score,

scores: {
  expression: data.scores.expression,
  structure: data.scores.structure,
  specificity: data.scores.specificity,
  jobFit: data.scores.job_fit,
  persuasiveness: data.scores.persuasiveness
},

strengths: Array.isArray(data.strengths)
  ? data.strengths
  : [],

improvements: Array.isArray(data.improvements)
  ? data.improvements
  : [],

keywords: Array.isArray(data.keywords)
  ? data.keywords
  : [],

recruiterComment:
  data.recruiter_comment || ""


};
}

/* ========================================
8. Result Rendering
======================================== */

function renderResult(result) {

document.querySelector("#total-score").textContent =
result.totalScore;

document.querySelector("#expression-score").textContent =
result.scores.expression;

document.querySelector("#structure-score").textContent =
result.scores.structure;

document.querySelector("#specificity-score").textContent =
result.scores.specificity;

document.querySelector("#job-fit-score").textContent =
result.scores.jobFit;

document.querySelector("#persuasiveness-score").textContent =
result.scores.persuasiveness;

document.querySelector("#expression-progress").style.width =
`${result.scores.expression}%`;

document.querySelector("#structure-progress").style.width =
`${result.scores.structure}%`;

document.querySelector("#specificity-progress").style.width =
`${result.scores.specificity}%`;

document.querySelector("#job-fit-progress").style.width =
`${result.scores.jobFit}%`;

document.querySelector("#persuasiveness-progress").style.width =
`${result.scores.persuasiveness}%`;

/* 잘된 점 */

const strengthsList =
document.querySelector("#strengths-list");

strengthsList.innerHTML = "";

result.strengths.forEach((item) => {

const li = document.createElement("li");

li.textContent = item;

strengthsList.appendChild(li);


});

/* 개선할 점 */

const improvementsList =
document.querySelector("#improvements-list");

improvementsList.innerHTML = "";

result.improvements.forEach((item) => {

const li = document.createElement("li");

li.textContent = item;

improvementsList.appendChild(li);


});

/* 추천 키워드 */

const keywordList =
document.querySelector("#keyword-list");

keywordList.innerHTML = "";

result.keywords.forEach((keyword) => {

const span = document.createElement("span");

span.className = "keyword";
span.textContent = keyword;

keywordList.appendChild(span);


});

/* 채용 담당자 한줄 평가 */

document.querySelector("#recruiter-comment").textContent =
"${result.recruiterComment}";
}

/* ========================================
9. Analyze Button
======================================== */

if (analyzeButton) {

analyzeButton.addEventListener("click", async () => {

hideFormMessage();


const job =
  jobInput.value.trim();

const question =
  questionInput.value.trim();

const essay =
  essayInput.value.trim();


/* 입력값 검사 */

if (!job) {

  showFormMessage(
    "지원 직무를 입력해주세요."
  );

  jobInput.focus();

  return;
}


if (!question) {

  showFormMessage(
    "자기소개서 문항을 입력해주세요."
  );

  questionInput.focus();

  return;
}


if (!essay) {

  showFormMessage(
    "자기소개서를 입력해주세요."
  );

  essayInput.focus();

  return;
}


/* 분석 중 상태 */

analyzeButton.disabled = true;
analyzeButton.textContent = "AI 분석 중...";


try {

  const response = await fetch(
    "/api/analyze",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        job: job,
        question: question,
        essay: essay
      })
    }
  );


  /* HTTP 에러 */

  if (!response.ok) {

    let errorMessage =
      "AI 분석 중 문제가 발생했습니다.";

    try {

      const errorData =
        await response.json();

      if (errorData.detail) {
        errorMessage = errorData.detail;
      }

    } catch (error) {
      // JSON 에러 응답이 아닐 경우 기본 메시지 사용
    }

    throw new Error(errorMessage);
  }


  /* JSON 결과 받기 */

  const data =
    await response.json();


  /* API 응답을 프론트 형식으로 변환 */

  const result =
    normalizeResult(data);


  /* 결과 화면 출력 */

  renderResult(result);


  /* 결과 페이지 이동 */

  showSection("result");


} catch (error) {

  console.error(
    "AI 분석 오류:",
    error
  );


  showFormMessage(
    error.message ||
    "AI 분석 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
  );


} finally {

  analyzeButton.disabled = false;

  analyzeButton.textContent =
    "AI 분석하기";

}


});

}

/* ========================================
10. Initial State
======================================== */

showSection("home");