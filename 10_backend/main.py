# FastAPI의 핵심 기능을 가져옵니다.
from fastapi import FastAPI, HTTPException, Query
# Pydantic은 데이터를 검증하고 구조를 정의하는 도구입니다. (매우 중요!)
from pydantic import BaseModel
# 리스트(배열) 타입을 정의하기 위해 가져옵니다.
from typing import List, Optional
# 비동기 통신(남의 API 호출할 때 내 서버 안 멈추게 하기)을 위한 핵심 라이브러리입니다.
import httpx

# FastAPI 앱 인스턴스를 생성합니다. 이게 우리 서버의 본체입니다.
app = FastAPI(
    title="AdGenius API",
    description="소상공인을 위한 AI 광고 영상 제작 에이전트 백엔드",
    version="1.0.0"
)

# ---------------------------------------------------------
# 1. 데이터 모델 정의 (DTO: Data Transfer Object)
# 프론트엔드(React)에게 어떤 모양의 데이터를 줄지 미리 약속하는 것입니다.
# ---------------------------------------------------------

class PromptCard(BaseModel):
    # 각 프롬프트 카드가 가질 데이터 구조입니다.
    id: str                 # 고유 ID (예: "0214-abcd...")
    image_url: str          # 이미지 주소 (Lexica 서버에 있는 이미지)
    prompt_text: str        # 우리가 가장 필요한 '프롬프트' 내용
    width: int              # 이미지 가로 길이
    height: int             # 이미지 세로 길이
    
    # 팁: Config 클래스를 쓰면 나중에 문서화할 때 예시 데이터를 보여줄 수 있습니다.
    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345",
                "image_url": "https://image.lexica.art/...",
                "prompt_text": "cinematic shot of a nike shoes, 4k",
                "width": 512,
                "height": 768
            }
        }

# ---------------------------------------------------------
# 2. API 라우터 (길 안내)
# 사용자가 어떤 주소로 들어오면 무슨 일을 할지 정합니다.
# ---------------------------------------------------------

@app.get("/")
def read_root():
    """
    서버가 살았는지 죽었는지 확인하는 기본 주소입니다.
    """
    return {"status": "online", "message": "AdGenius Backend is Running!"}


@app.get("/api/prompts/trending", response_model=List[PromptCard])
async def get_trending_prompts(q: str = Query("advertisement", description="검색할 키워드")):
    """
    [기능 설명]
    외부 API(Lexica.art)를 호출해서 '광고(advertisement)'와 관련된
    고퀄리티 프롬프트와 이미지 목록을 가져옵니다.
    
    [파라미터]
    - q: 검색어 (기본값은 'advertisement')
    """
    
    # 1. Lexica API 주소 설정 (여기로 요청을 보낼 겁니다)
    lexica_url = f"https://lexica.art/api/v1/search?q={q}"
    
    print(f"DEBUG: Lexica API 호출 시작 -> {lexica_url}") # 로그 찍기

    # 2. 비동기 클라이언트 시작 (with 문을 쓰면 사용 후 자동으로 닫아줍니다)
    async with httpx.AsyncClient() as client:
        try:
            # 3. 실제 요청 보내기 (await: "응답 올 때까지 다른 일 하면서 기다릴게")
            # timeout=15.0 : 15초가 지나도 응답 없으면 에러 내고 끊어라 (무한대기 방지)
            response = await client.get(lexica_url, timeout=15.0)
            
            # 4. 상태 코드 확인 (200 OK가 아니면 에러 발생시킴)
            response.raise_for_status()
            
            # 5. 받은 JSON 데이터 꺼내기
            data = response.json()
            
            # Lexica API는 결과 이미지를 "images"라는 리스트 안에 담아줍니다.
            # 만약 "images" 키가 없으면 빈 리스트 []를 반환합니다.
            images_raw = data.get("images", [])
            
            # 6. 데이터 가공 (필요한 것만 쏙쏙 뽑아서 내 입맛대로 포장하기)
            results = []
            
            # 최대 30개까지만 가져오겠습니다. (너무 많으면 느려짐)
            for img in images_raw[:30]:
                # 가끔 데이터가 불완전한 경우가 있어서 안전하게 가져옵니다.
                if img.get("src") and img.get("prompt"):
                    card = PromptCard(
                        id=img["id"],
                        image_url=img["src"],       # Lexica의 src가 이미지 주소입니다.
                        prompt_text=img["prompt"],  # 사용자가 복사할 프롬프트
                        width=img["width"],
                        height=img["height"]
                    )
                    results.append(card)
            
            print(f"DEBUG: 총 {len(results)}개의 데이터를 가져왔습니다.")
            return results

        # 7. 에러 처리 (실무에서 매우 중요!)
        except httpx.HTTPStatusError as e:
            # 외부 서버가 404, 500 등 에러를 뱉었을 때
            print(f"Error: Lexica API 상태 오류 - {e}")
            raise HTTPException(status_code=503, detail="외부 이미지 서버에 연결할 수 없습니다.")
            
        except httpx.RequestError as e:
            # 인터넷이 끊겼거나 주소가 잘못됐을 때
            print(f"Error: 요청 실패 - {e}")
            raise HTTPException(status_code=503, detail="네트워크 연결을 확인해주세요.")
            
        except Exception as e:
            # 그 외 예상치 못한 모든 에러
            print(f"Error: 알 수 없는 오류 - {e}")
            raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

# 이 파일이 직접 실행될 때만 서버를 켭니다. (터미널 명령어 대용)
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0"은 외부 접속 허용, port=8000번 사용, reload=True는 코드 수정 시 자동 재시작
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)