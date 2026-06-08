import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="부경대 AI 응용 프로그래밍 과제",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 실습 1: 기본 LLM 질의응답")
st.markdown("---")

# 1. 세션 상태(session_state)에 API Key 초기화
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

# 2. 비밀번호 형태로 API Key 입력 받기 (페이지를 이동해도 유지됨)
api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요:",
    type="password",
    value=st.session_state["openai_api_key"],
    placeholder="sk-..."
)

if api_key_input:
    st.session_state["openai_api_key"] = api_key_input

st.info("💡 여기서 입력한 API Key는 왼쪽 사이드바 메뉴를 통해 다른 페이지로 이동해도 안전하게 유지됩니다.")

# 3. @st.cache_data를 이용한 응답 캐싱 (동일한 질문은 재실행 시 저장된 결과 반환)
@st.cache_data(show_spinner="GPT가 답변을 생성하는 중입니다...")
def get_llm_response(api_key, question):
    if not api_key:
        return "사이드바나 메인 화면에서 API Key를 먼저 입력해주세요."
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류가 발생했습니다: {e}"

# 4. 사용자 질문 입력 및 출력
st.subheader("💡 일반 캐싱 질문하기")
user_question = st.text_input("GPT에게 궁금한 점을 물어보세요:")

if st.button("질문 전송"):
    if not st.session_state["openai_api_key"]:
        st.error("API Key를 입력해야 질문을 보낼 수 있습니다.")
    elif user_question:
        result = get_llm_response(st.session_state["openai_api_key"], user_question)
        st.markdown("### 📝 답변 결과")
        st.write(result)
    else:
        st.warning("질문 내용을 입력해주세요.")

  import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="실습 2: 일반 Chat", page_icon="💬")
st.title("💬 실습 2: 연속 대화 챗봇")
st.markdown("---")

# 메인 페이지에서 공유된 API Key 가져오기
api_key = st.session_state.get("openai_api_key", "")

if not api_key:
    st.warning("⚠️ 메인 페이지(app.py)에서 OpenAI API Key를 먼저 입력해주세요.")
else:
    # 1. 대화 기록을 저장할 세션 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Clear 버튼 구현 (대화 내용 삭제 후 새로운 대화 시작)
    if st.button("🗑️ Clear (대화 초기화)"):
        st.session_state.messages = []
        st.rerun()

    # 기존 대화 기록 출력
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. 사용자 입력창 및 OpenAI API 연동 (스트리밍 적용)
    if prompt := st.chat_input("무엇이든 물어보세요!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            client = OpenAI(api_key=api_key)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

  import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="실습 3: 부경대 도서관 챗봇", page_icon="📚")
st.title("📚 실습 3: 국립부경대학교 도서관 챗봇")
st.markdown("---")

# 부경대 도서관 규정 요약 텍스트 문자열 저장 (도서관 휴관일 및 학부생 대출 규정 포함)
LIBRARY_REGULATIONS = """
[국립부경대학교 도서관 운영 규정]

제11조(휴관일) 
도서관의 휴관일은 다음 각 호와 같다.
1. 관공서의 공휴일 (단, 일요일은 대학원생 및 학부생 열람실 이용에 한해 별도 지정 가능)
2. 본교 개교기념일
3. 기타 도서관장이 필요하다고 인정하여 지정하는 날 (임시휴관일)

제15조(대출 권수 및 기간) 
자료의 대출 권수와 기간은 다음 각 호와 같다.
1. 전임교원: 30권 / 90일
2. 대학원생 및 시간강사: 10권 / 30일
3. 학부생 (재학생): 5권 / 10일
4. 조교 및 사내 직원: 10권 / 30일
"""

api_key = st.session_state.get("openai_api_key", "")

if not api_key:
    st.warning("⚠️ 메인 페이지(app.py)에서 OpenAI API Key를 먼저 입력해주세요.")
else:
    if "lib_messages" not in st.session_state:
        st.session_state.lib_messages = []

    if st.button("🗑️ 대화 초기화 (Clear)"):
        st.session_state.lib_messages = []
        st.rerun()

    # 기존 도서관 대화 내용 출력
    for message in st.session_state.lib_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 질문 받기
    if prompt := st.chat_input("부경대 도서관 규정에 대해 물어보세요! (예: 학부생 책 대여는 몇 권까지인가요?)"):
        st.session_state.lib_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            client = OpenAI(api_key=api_key)
            
            # system 역할을 명시하여 규정집 데이터만을 근거로 대답하도록 제약 조건 부여
            system_instruction = {
                "role": "system",
                "content": f"너는 국립부경대학교 도서관 안내 챗봇이야. 친절하게 답변하되, 반드시 아래 제공된 [도서관 규정] 내용을 바탕으로만 정확하게 답변해줘. 규정에 나와있지 않은 정보는 잘 모른다고 정중하게 답변해줘.\n\n[도서관 규정]\n{LIBRARY_REGULATIONS}"
            }
            
            messages = [system_instruction] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.lib_messages
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

st.set_page_config(page_title="실습 4: ChatPDF", page_icon="📄")
st.title("📄 실습 4: ChatPDF (OpenAI File Search)")
st.markdown("---")

api_key = st.session_state.get("openai_api_key", "")

if not api_key:
    st.warning("⚠️ 메인 페이지(app.py)에서 OpenAI API Key를 먼저 입력해주세요.")
else:
    client = OpenAI(api_key=api_key)

    # Assistants 관련 ID 세션 초기화
    if "asst_id" not in st.session_state: st.session_state.asst_id = None
    if "thread_id" not in st.session_state: st.session_state.thread_id = None
    if "vs_id" not in st.session_state: st.session_state.vs_id = None
    if "pdf_messages" not in st.session_state: st.session_state.pdf_messages = []

    # 단일 PDF 파일 업로드 인터페이스
    uploaded_file = st.file_uploader("PDF 파일을 하나 업로드하세요", type=["pdf"], accept_multiple_files=False)

    # Clear 버튼 구현 (서버에 남아있는 Assistant와 Vector Store를 명시적으로 삭제)
    if st.button("🗑️ PDF 대화 종료 및 벡터 스토어 삭제 (Clear)"):
        with st.spinner("OpenAI 서버 자원 해제 중..."):
            if st.session_state.asst_id:
                try: client.beta.assistants.delete(st.session_state.asst_id)
                except: pass
            if st.session_state.vs_id:
                try: client.beta.vector_stores.delete(st.session_state.vs_id)
                except: pass
            
            st.session_state.asst_id = None
            st.session_state.thread_id = None
            st.session_state.vs_id = None
            st.session_state.pdf_messages = []
            st.success("모든 대화 및 벡터 데이터가 초기화되었습니다.")
            st.rerun()

    # 파일 업로드 직후 OpenAI Assistants & File Search 리소스 빌드
    if uploaded_file and not st.session_state.asst_id:
        with st.spinner("PDF 문서를 읽고 의미를 분석(인덱싱)하는 중입니다..."):
            # 1. 파일 생성
            openai_file = client.files.create(file=uploaded_file, purpose="assistants")
            
            # 2. 벡터 스토어 빌드 및 파일 매핑
            vector_store = client.beta.vector_stores.create(name=f"Asst_VS_{uploaded_file.name}")
            client.beta.vector_stores.files.create(vector_store_id=vector_store.id, file_id=openai_file.id)
            
            # 3. File Search 도구를 사용하는 어시스턴트 정의
            assistant = client.beta.assistants.create(
                name="PDF 문서 분석가",
                instructions="제공된 PDF 문서 파일 내용을 면밀히 분석하여 질문에 올바르게 답변하세요.",
                model="gpt-4o-mini",
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
            )
            
            # 4. 독립된 대화 룸(스레드) 개설
            thread = client.beta.threads.create()
            
            # 세션 스테이트 기록
            st.session_state.asst_id = assistant.id
            st.session_state.vs_id = vector_store.id
            st.session_state.thread_id = thread.id
            st.success("🎉 준비 완료! 업로드하신 문서 내용에 대해 질문해 보세요.")

    # 대화 히스토리 화면 출력
    for msg in st.session_state.pdf_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 질의응답 처리 루프
    if st.session_state.asst_id and (prompt := st.chat_input("문서 내용에 대해 질문하기:")):
        st.session_state.pdf_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 사용자 입력을 스레드에 추가
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # 런(Run) 구동 및 폴링 대기
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.asst_id
        )

        with st.chat_message("assistant"):
            with st.spinner("문서 본문 검색 및 요약 중..."):
                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
                
                if run.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                    ans_content = messages.data[0].content[0].text.value
                    st.markdown(ans_content)
                    st.session_state.pdf_messages.append({"role": "assistant", "content": ans_content})
                else:
                    st.error(f"오류가 발생했습니다. 상태: {run.status}")
