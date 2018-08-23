# -*- coding: utf-8 -*-
# 인터파크 투어 사이트에서 여행지를 입력후 검색 -> 잠시후 -> 결과
# 로그인시 pc 웹 사이트에서 처리가 어려울 경우 -> 모바일 로그인 진입 ->
# 모듈 가져오기
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
# 명시적 대기를 위해
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import  sys
import time
from Tour import TourInfo
from bs4 import BeautifulSoup as bs
from DBMgr import  DBHelper as Db


reload(sys)
sys.setdefaultencoding('utf-8')

# 사전에 필요한 정보를 로드 -> 디비 혹은 쉘, 배치 파일에서 인자로 받아서 세팅
main_url = 'http://tour.interpark.com/'
keyword = '로마'
keywords= unicode(keyword)
tour_list = []
db = Db()

# 드라아버 로드
driver = wd.Chrome(executable_path='chromedriver.exe')
# 차후 -> 옵션 부여하여 (프록시, 에이전트 조작, 이미지를 배제)
# 크롤링을 오래돌리면 -> 임시파일들이 쌓인다!!-> 템포 파일 삭제

# 사이트 접속 (get)
driver.get(main_url)
# 검색창을 찾아서 검색어 입력
# id : SearchGNBText
driver.find_element_by_id('SearchGNBText').send_keys(keywords)
# 수정할 경우 -> 뒤에 내용이 붙어버림 => .clear() -> send_keys()
# 검색 버튼 클릭
driver.find_element_by_css_selector('button.search-btn').click()

# 잠시 대기 -> 페이지가 로드되고 나서 즉각적으로 데이터를 획득 하는 행위는
# 명시적 대기 -> 특정 요소가 로케이트(발견 될때까지) 대기
# 암시적 대기 -> DOM이 다 로드 될때까지 대기 하고 먼저 로드되면 바로 진행
# 절대적 대기 - > time.sleep(10) -> 클라우드 페어(디도스 방어, 솔루션)
try:
    element = WebDriverWait(driver,10).until(
        # 지정한 한개 요소가 올라오면 웨이트 종료
        EC.presence_of_element_located((By.CLASS_NAME,'oTravelBox'))
    )
except Exception as e:
    print('error', e)

# 암시적 대기 -> DOM이 다 로드 될때까지 대기 하고 먼저 로드되면 바로 진행
# 요소를 찾을 특정 시간 동안 dom 풀링을 지시 예를 들어 10초이내라도 발견되면 진행
driver.implicitly_wait(10)
# 절대적 대기 - > time.sleep(10) -> 클라우드 페어(디도스 방어, 솔루션)
# 더보기 눌러서 -> 게시판 진입 자제
driver.find_element_by_css_selector('.oTravelBox>.boxList>.moreBtnWrap>.moreBtn').click()

# 게시판에서 데이터를 가져올때
# 데이터가 많으면 세션( 혹시 로그인을 해서 접근되서 사이트일 경우) 관리
# 특정 단위별로 로그아웃 로그인 계속 시도
# 특정 게시물이 사라질 경우 -> 팝업 발생 -> 팝업처리 검토
# 게시판 스캔시 -> 임계점을 모름 !!
# 게시판 스캔 -> 메타정보 획득 -> loop를 돌려서 일관적으로 방문 접근 처리

# searchModule.SetCategoryList(2, '')

for page in range(1,2):
    try:
        # javascript action
        driver.execute_script("searchModule.SetCategoryList(%s,'')" % page)
        time.sleep(2)
        # 상품명, 코멘트 ,기간1, 기간2 ,가격,평점 ,썸네일, 링크(상품상세정보)
        boxItems = driver.find_elements_by_css_selector('.oTravelBox>.boxList>.boxItem')
        for li in boxItems:

            obj = TourInfo(
                li.find_element_by_css_selector('h5.proTit').text,
                li.find_element_by_css_selector('.proPrice').text,
                li.find_elements_by_css_selector('.info-row .proInfo')[1].text,
                li.find_element_by_css_selector('a').get_attribute('onclick'),
                li.find_element_by_css_selector('img').get_attribute('src')
            )
            tour_list.append( obj )
    except Exception as e1 :
        print('error', e1)

# 수집한 정보 개수를 루프 -> 페이지 방문 -> 콘텐츠 획득(상품상제정보)
for tour in tour_list:
    # 링크데이터에서 실데이터 획득
    arr=tour.link.split(',')
    if arr :
        link= arr[0].replace('searchModule.OnClickDetail(','')
        detail_url = link[1:-1]
        driver.get(detail_url)
        time.sleep(2)

        # 현재 페이지를 beautifulsoup 의 DOM으로 구성
        # page_source -> 현재 페이지
        soup = bs(driver.page_source,'html.parser')
        data =soup.select('.tip-cover')

        # 디비 입력
        content_final = ''
        for c in data[0].contents:
             content_final += str(c)


        # # html 콘첸츠 데이터 전처리 (디비에 입력 가능토록)
        import re

        content_final = re.sub("'", '"', content_final)
        content_final = re.sub(re.compile(r'\r\n|\r|\n|\n\r+'), '', content_final)

        # 콘텐츠 내용에 따라 전처리 => data[0].contents
        db.db_insertCrawlingData(
             tour.title,
             tour.price[:-1],
             tour.area.replace('출발 가능 기간 : ',''),
             content_final,
             keyword
         )

# 종료
driver.close()
driver.quit()

sys.exit()