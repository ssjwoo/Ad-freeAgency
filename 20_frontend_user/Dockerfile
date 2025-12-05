# 1. 노드 20버전(LTS) 리눅스 환경 사용
FROM node:20-alpine

# 2. 작업 폴더 지정
WORKDIR /app

# 3. 패키지 설정 파일 복사 (캐시 활용을 위해 먼저 복사)
COPY package.json package-lock.json ./

# 4. 라이브러리 설치
RUN npm install

# 5. 소스 코드 전체 복사
COPY . .

# 6. Vite 서버 포트 개방 (5173)
EXPOSE 5173

# 7. 개발 서버 실행 (호스트 연결 허용 옵션 --host 필수)
CMD ["npm", "run", "dev", "--", "--host"]