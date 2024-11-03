import streamlit as st
import feedparser
import pandas as pd
from deep_translator import GoogleTranslator
from datetime import datetime
import re

def clean_html(text):
    """HTML 태그 제거"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def translate_text(text):
    """텍스트 번역 함수"""
    try:
        # 빈 텍스트 체크
        if not text or text.isspace():
            return ""
            
        # 텍스트가 너무 길 경우 나눠서 번역
        max_length = 4500  # Google 번역 제한
        if len(text) > max_length:
            parts = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            translated_parts = []
            for part in parts:
                if part and not part.isspace():
                    translated = GoogleTranslator(source='en', target='ko').translate(text=part)
                    translated_parts.append(translated)
            return ' '.join(translated_parts)
        else:
            if text and not text.isspace():
                return GoogleTranslator(source='en', target='ko').translate(text=text)
            return ""
    except Exception as e:
        st.error(f"번역 오류: {str(e)}")
        return f"번역 실패: {text[:100]}..."

def format_date(date_str):
    """날짜 형식 변환"""
    try:
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d %H:%M')
    except:
        return date_str

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="TechCrunch 뉴스 번역기",
        page_icon="🌐",
        layout="wide"
    )
    
    # 제목과 설명
    st.title("🌐 TechCrunch 뉴스 번역기")
    st.markdown("TechCrunch의 최신 기술 뉴스를 한국어로 번역해서 보여드립니다.")
    
    # TechCrunch RSS 피드 URL
    techcrunch_feed = "https://techcrunch.com/feed/"
    
    try:
        with st.spinner('뉴스를 불러오고 번역하는 중입니다...'):
            # RSS 피드 파싱
            feed = feedparser.parse(techcrunch_feed)
            
            # 데이터 추출 및 번역
            feed_data = []
            
            # 진행 상태 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, entry in enumerate(feed.entries[:10]):
                status_text.text(f'{i+1}/10 기사 처리 중...')
                
                # 제목 번역
                title = clean_html(entry.title)
                translated_title = translate_text(title)
                
                # 요약 번역
                description = clean_html(entry.get('description', ''))
                translated_description = translate_text(description) if description else ''
                
                # 날짜 처리
                published = entry.get('published', entry.get('updated', 'No date'))
                formatted_date = format_date(published)
                
                feed_data.append({
                    '원문 제목': title,
                    '번역 제목': translated_title,
                    '날짜': formatted_date,
                    '원문 내용': description,
                    '번역 내용': translated_description,
                    '링크': entry.link
                })
                
                # 진행률 업데이트
                progress_bar.progress((i + 1) / 10)
            
            # 진행 상태 표시 제거
            progress_bar.empty()
            status_text.empty()
            
            # 뉴스 표시
            st.markdown("### 📰 최신 뉴스")
            
            # 각 뉴스 항목을 expander로 표시
            for idx, item in enumerate(feed_data, 1):
                with st.expander(f"#{idx}. {item['번역 제목']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📝 원문")
                        st.subheader(item['원문 제목'])
                        st.write(item['원문 내용'])
                    
                    with col2:
                        st.subheader("🔄 번역")
                        st.subheader(item['번역 제목'])
                        st.write(item['번역 내용'])
                    
                    st.write(f"📅 게시일: {item['날짜']}")
                    st.markdown(f"🔗 [기사 링크]({item['링크']})")
            
            # CSV 다운로드 옵션
            st.markdown("### 💾 데이터 다운로드")
            df = pd.DataFrame(feed_data)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 번역 결과 CSV로 다운로드",
                data=csv,
                file_name="techcrunch_translated_news.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        st.markdown("새로고침을 해보시거나, 잠시 후 다시 시도해주세요.")

if __name__ == '__main__':
    main()
