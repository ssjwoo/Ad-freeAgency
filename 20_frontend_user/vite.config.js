import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' // (참고: 아까 설치 방식에 따라 다를 수 있음. 본인 코드 유지)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()], // 기존 플러그인 설정 유지
  server: {
    host: true, // 👈 이 줄을 꼭 추가해야 도커 밖에서 접속 가능!!!
    port: 5173,
    watch: {
      usePolling: true // 윈도우-도커 간 파일 동기화 버그 방지
    }
  }
})