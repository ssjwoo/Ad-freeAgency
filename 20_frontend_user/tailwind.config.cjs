/** @type {import('tailwindcss').Config} */
module.exports = {
  // content: Tailwind가 클래스 이름을 찾을 파일 경로들을 지정합니다.
  content: [
    "./index.html",                  // 1. 최상위 index.html 파일도 감시 대상에 포함
    "./src/**/*.{js,ts,jsx,tsx}",    // 2. src 폴더 안에 있는 모든 js, ts, jsx, tsx 파일을 감시 (핵심!)
  ],
  theme: {
    extend: {
      // 여기에 색상이나 폰트 등 커스텀 설정을 추가할 수 있습니다. (지금은 기본값 사용)
    },
  },
  plugins: [
    // 플러그인이 필요하면 여기에 추가합니다. (지금은 없음)
  ],
}