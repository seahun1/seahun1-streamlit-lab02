your_project/
│
├── app.py              # 메인 페이지 (실습 1)
└── pages/
    ├── 1_Chat.py       # 실습 2 페이지
    ├── 2_Library.py    # 실습 3 페이지
    └── 3_ChatPDF.py    # 실습 4 페이지

  pip install streamlit openai pypdf

  import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="LLM Q&A 앱", layout="centered")
st.title("🤖 기본 LLM 질의응답")

# 1. session_state에 API Key 초기화 및 저장
if "openai_api_key" not in st.st.session_state:
    st.session_state["openai_api_key"] = ""

# 비밀번호 형태로 입력 받기
api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요:", 
    type="password", 
    value=st.session_state["openai_api_key"]
)

if api_key_input:
    st.session_state["openai_api_key"] = api_key_input

# 2. @st.cache_data를 이용한 응답 캐싱 (동일 질문 리턴 방지)
@st.cache_data(show_spinner="답변을 생성 중입니다...")
def get_llm_response(api_key, question):
    if not api_key:
        return "API Key를 입력해주세요."
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 비용 효율적인 최신 모델 권장
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류가 발생했습니다: {e}"

# 3. 사용자 질문 입력 및 출력
user_question = st.text_input("질문을 입력하세요:")
if st.button("질문하기"):
    if user_question:
        result = get_llm_response(st.session_state["openai_api_key"], user_question)
        st.markdown("### 📝 답변")
        st.write(result)
    else:
        st.warning("질문을 입력해주세요.")

  import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot 페이지")

# 메인 페이지에서 저장된 API Key 가져오기
api_key = st.session_state.get("openai_api_key", "")

if not api_key:
    st.warning("메인 페이지에서 OpenAI API Key를 먼저 입력해주세요.")
else:
    # 1. 대화 히스토리 session_state 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Clear 버튼 구현 (대화 내용 삭제)
    if st.button("Clear (대화 초기화)"):
        st.session_state.messages = []
        st.rerun()

    # 기존 대화 내용 화면에 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. 사용자 입력 및 OpenAI API 연동
    if prompt := st.chat_input("무엇이든 물어보세요!"):
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성 및 표시
        with st.chat_message("assistant"):
            client = OpenAI(api_key=api_key)
            
            # 스트리밍 응답 적용 (선택 사항이지만 더 나은 UX 제공)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        
        # AI 응답 히스토리에 추가
        st.session_state.messages.append({"role": "assistant", "content": response})

  import streamlit as st
from openai import OpenAI

st.title("📚 국립부경대학교 도서관 챗봇")

# 실제 규정집 내용을 긁어서 아래 변수에 넣으세요.
LIBRARY_REGULATIONS = """
[국립부경대학교 도서관 규정 요약 예시]
제11조(휴관일) 도서관의 휴관일은 다음 각 호와 같다.
1. 관공서의 공휴일
2. 개교기념일
3. 기타 관장이 필요하다고 인정하여 지정하는 날

제15조(대출 책수 및 기간) 
1. 학부생: 5권, 10일 간 대출 가능
2. 대학원생: 10권, 30일 간 대출 가능
""" [cite: 23, 26]

api_key = st.session_state.get("openai_api_key", "")

if not api_key:
    st.warning("메인 페이지에서 OpenAI API Key를 먼저 입력해주세요.")
else:
    if "lib_messages" not in st.session_state:
        st.session_state.lib_messages = []

    # 화면 표시
    for message in st.session_state.lib_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("도서관 규정에 대해 물어보세요! (예: 학부생 책 대여 권수?)"):
        st.session_state.lib_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            client = OpenAI(api_key=api_key)
            
            # System 가이드에 규정집을 주입하여 답변을 제한함
            messages = [
                {
                    "role": "system", 
                    "content": f"너는 국립부경대학교 도서관 챗봇이야. 아래 제공된 도서관 규정집 내용을 바탕으로만 정확하게 답변해줘. 규정에 없는 내용은 모른다고 답해줘.\n\n[규정집]\n{LIBRARY_REGULATIONS}"
                }
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.lib_messages
            ]
            
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
            )
            response = st.write_stream(stream)
            
        st.session_state.lib_messages.append({"role": "assistant", "content": response})

  import streamlit as st
from openai import OpenAI
import time

st.title("📄 ChatPDF (OpenAI File Search)")

api_key = st.session_state.get("openai_api_key", "")

if not api_key:
    st.warning("메인 페이지에서 OpenAI API Key를 먼저 입력해주세요.")
else:
    client = OpenAI(api_key=api_key)

    # 세션 상태 변수 초기화
    if "assistant_id" not in st.session_state: st.session_state.assistant_id = None
    if "thread_id" not in st.session_state: st.session_state.thread_id = None
    if "vector_store_id" not in st.session_state: st.session_state.vector_store_id = None
    if "pdf_messages" not in st.session_state: st.session_state.pdf_messages = []

    # 1. 파일 업로더 생성 (하나만 입력 받음)
    uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"], accept_multiple_files=False)

    # 2. Clear 버튼 구현 (생성된 OpenAI 리소스 삭제 및 초기화)
    if st.button("Clear 및 벡터 스토어 삭제"):
        if st.session_state.assistant_id:
            try: client.beta.assistants.delete(st.session_state.assistant_id)
            except: pass
        if st.session_state.vector_store_id:
            try: client.beta.vector_stores.delete(st.session_state.vector_store_id)
            except: pass
        
        st.session_state.assistant_id = None
        st.session_state.thread_id = None
        st.session_state.vector_store_id = None
        st.session_state.pdf_messages = []
        st.success("모든 벡터 스토어와 대화가 초기화되었습니다!")
        st.rerun()

    # 3. 파일이 업로드되었고, 아직 처리되지 않았다면 OpenAI File Search 세팅
    if uploaded_file and not st.session_state.assistant_id:
        with st.spinner("파일을 분석하고 벡터 스토어를 생성 중입니다..."):
            # 임시 파일로 저장 후 OpenAI에 업로드
            openai_file = client.files.create(file=uploaded_file, purpose="assistants")
            
            # 벡터 스토어 생성 및 파일 링크
            vector_store = client.beta.vector_stores.create(name=f"VS_{uploaded_file.name}")
            client.beta.vector_stores.files.create(vector_store_id=vector_store.id, file_id=openai_file.id)
            
            # File Search 기능이 활성화된 Assistant 생성
            assistant = client.beta.assistants.create(
                name="PDF QA Assistant",
                instructions="주어진 문서의 내용을 기반으로 질문에 성실히 답변하세요.",
                model="gpt-4o-mini",
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
            )
            
            # 대화 스레드 생성
            thread = client.beta.threads.create()
            
            # ID 저장
            st.session_state.assistant_id = assistant.id
            st.session_state.vector_store_id = vector_store.id
            st.session_state.thread_id = thread.id
            st.success("파일 분석 완료! 대화를 시작해보세요.")

    # 대화 UI 출력
    for msg in st.session_state.pdf_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 4. 질의응답 진행
    if st.session_state.assistant_id and (prompt := st.chat_input("PDF 내용에 대해 질문하세요:")):
        st.session_state.pdf_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 사용자의 메시지를 OpenAI 스레드에 추가
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Assistant 실행 (Run)
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        # 완료될 때까지 대기 (Polling)
        with st.chat_message("assistant"):
            with st.spinner("답변을 찾는 중..."):
                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
                
                if run.status == "completed":
                    # 최신 답변 가져오기
                    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                    ans_content = messages.data[0].content[0].text.value
                    st.markdown(ans_content)
                    st.session_state.pdf_messages.append({"role": "assistant", "content": ans_content})
                else:
                    st.error("답변 생성에 실패했습니다.")

              
