import streamlit as st
import feedparser
import pandas as pd
from googletrans import Translator
from datetime import datetime
import re

def translate_text(text, translator):
    try:
        result = translator.translate(text, src='en', dest='ko')
        return result.text
    except:
        return f"번역 실패: {text}"

def clean_html(text):
    # HTML 태그 제거
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def main():
    st.title("TechCrunch 뉴스 번역기")
    
    # 번역기 초기화
    translator = Translator()
    
    # TechCrunch RSS 피드 URL
    techcrunch_feed = "https://techcrunch.com/feed/"
    
    try:
        with st.spinner('피드를 불러오는 중...'):
            # RSS 피드 파싱
            feed = feedparser.parse(techcrunch_feed)
            
            # 데이터 추출 및 번역
            feed_data = []
            for entry in feed.entries[:10]:  # 최근 10개 글만 가져오기
                # 제목 번역
                translated_title = translate_text(entry.title, translator)
                
                # 요약 번역 (description이 있는 경우)
                description = entry.get('description', '')
                translated_description = translate_text(description, translator) if description else ''
                
                published = entry.get('published', entry.get('updated', 'No date'))
                try:
                    date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d %H:%M')
                except:
                    date = published
                
                feed_data.append({
                    '원문 제목': entry.title,
                    '번역 제목': translated_title,
                    '날짜': date,
                    '원문 내용': description,
                    '번역 내용': translated_description,
                    '링크': entry.link
                })
            
            # 각 뉴스 항목을 expander로 표시
            for idx, item in enumerate(feed_data, 1):
                with st.expander(f"#{idx}. {item['번역 제목']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("원문")
                        st.subheader(item['원문 제목'])
                        st.write(clean_html(item['원문 내용']))
                    
                    with col2:
                        st.subheader("번역")
                        st.subheader(item['번역 제목'])
                        st.write(clean_html(item['번역 내용']))
                    
                    st.write(f"게시일: {item['날짜']}")
                    st.markdown(f"[기사 링크]({item['링크']})")
            
            # 데이터프레임 생성 및 CSV 다운로드 옵션
            df = pd.DataFrame(feed_data)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="번역 결과 CSV로 다운로드",
                data=csv,
                file_name="techcrunch_translated_news.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == '__main__':
    main() 
