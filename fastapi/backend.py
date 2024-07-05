import requests
from bs4 import BeautifulSoup
import fake_useragent
import time


ua = fake_useragent.UserAgent()


def get_links(criteria: str):
    try:
        data = requests.get(
            url=f"https://hh.ru/search/vacancy?text={criteria}&salary=&ored_clusters=true&page=1",
            headers = {"user-agent": ua.random}
        )
        if data.status_code != 200:
            return
        soup = BeautifulSoup(data.content, 'lxml')
        try:
            page_count = int(soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find("span").text)
        except:
            return
        for page in range(page_count):
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={criteria}&salary=&ored_clusters=true&page={page}",
                headers={"user-agent": ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, 'lxml')
            v_count = soup.find_all("span", attrs={"class": "serp-item__title-link-wrapper"})
            for span in range(len(v_count)):
                a = soup.find_all("span", attrs={"class": "serp-item__title-link-wrapper"})[span].find("a")
                yield f"{a.attrs['href']}"

    except Exception as e:
        print(f'{e}')
    time.sleep(1)


def get_vacancy(link: str) -> list[str]:
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        name = soup.find(attrs={"class": "bloko-header-section-1"}).text
    except:
        name = ""
    try:
        salary = soup.find(attrs={"data-qa": "vacancy-salary"}).text.replace("\xa0","")
    except:
        salary = ""
    try:
        experience = soup.find(attrs={"data-qa": "vacancy-experience"}).text
    except:
        experience = ""
    try:
        employer = soup.find(attrs={"data-qa": "bloko-header-2"}).text.replace("\xa0","")
    except:
        employer = ""
    try:
        tags = "&".join([tag.text for tag in soup.find_all(attrs={"class": "magritte-tag__label___YHV-o_3-0-0"})])
    except:
        tags = ""
    vacancy = [name, salary, experience, employer, tags, str(link)]
    return vacancy
