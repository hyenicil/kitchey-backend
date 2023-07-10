import requests
import csv
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
web= 'https://yemek.com/tarif/'

options = Options()
options.add_argument("--headless=new")
driver= webdriver.Chrome('chromedriver_win32/chromedriver')
response = driver.get(web)
recipeId = ''
recipeName = ''
recipeType = ''
recipeMaterial = ''
recipeCount = ''
recipePreparationTime = ''
recipeCookingTime = ''
recipeDescription = ''
#//////////////////////
recipeIdList = []
recipeNameList = []
recipeTypeList = []
recipeMaterialList = []
recipeMaterialIdList = []
recipeCountList = []
recipePreparationTimeList = []
recipeCookingTimeList = []
recipeRecipeList = []
materialList = []
materialIdList = []
data_dict={}
dataMaterialList=[]



with open ('C:\\MachineLearning\\Bİtirme Projesi\\Deneme-1\\ingredients.csv','r',encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        data_dict[row['id']] = row['ingredients']

for x in range(30000):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    if x == 29999:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            recipeInfo = soup.find('div', {'class': 'infinite-scroll-component overflow-hidden mt-3'})\
                .find_all('h4',attrs={'BoxContent_boxTitle__xIYek'})
            recipeLinkList = ['https://yemek.com' + recipeLink.a.get('href') for recipeLink in recipeInfo]
            recipeNamesList = [name.text.strip() for name in recipeInfo]
            print(len(recipeLinkList), len(recipeNamesList))
            for i in range(len(recipeLinkList)):
                recipeName= recipeNamesList[i]
                recipePage = requests.get(recipeLinkList[i], timeout=None)
                soup = BeautifulSoup(recipePage.text, 'html.parser')
                recipePageInfos= soup.find_all(class_='ContentRecipe_recipeDetail__0EBU0')
                if recipePageInfos is not None:
                    for info in recipePageInfos:
                        if info.find('h3').text == 'KAÇ KİŞİLİK':
                            recipeCount = info.find('span').text
                        if info.find('h3').text == 'HAZIRLAMA SÜRESİ':
                            recipePreparationTime = info.find('span').text
                        if info.find('h3').text == 'PİŞİRME SÜRESİ':
                            recipeCookingTime = info.find('span').text
                recipeInfoType = soup.find('div', 'Breadcrumb_breadcrumbs__ZnTLV')
                if recipeInfoType is not None:
                    recipeInfoType = soup.find('div', 'Breadcrumb_breadcrumbs__ZnTLV').find_all('div','d-flex align-items-center')
                    recipeType = recipeInfoType[len(recipeInfoType)-1].text
                else:
                    recipeType = '-'
                recipeInfoDescription = soup.find('div', 'Ingredients_ingredients__hk2Pb')
                if recipeInfoDescription is not None:
                    recipeMaterialsLine = recipeInfoDescription.find_all("li")
                else:
                    recipeMaterialsLine  = []
                    print("Ingredients_ingredients__hk2Pb sınıfı bulunamadı.")



                recipeDescriptions = soup.find_all(class_='ContentRecipe_instructions__yZRS_')
                exceptStatus = False
                for recipeEntity in recipeMaterialsLine:  #Ürünler
                    y = 0
                    entity = ''
                    founded = False
                    for recipeM in recipeEntity("span"):
                        entity = recipeM.text.strip()
                        if y == 2:
                            e = recipeM.text.strip()
                            for ing in data_dict:
                                if e.find(data_dict[ing]) != -1:
                                    founded = True
                                    materialList.append(e)
                                    materialIdList.append(ing)
                                    break
                            if founded == False:
                                dataMaterialList.append(e)

                        y += 1
                if len(recipeMaterialsLine) != len(materialList):
                    materialList.clear()
                    materialIdList.clear()
                #if exceptStatus == True:
                    continue
                else:
                    description = ''
                    for recipeD in recipeDescriptions:
                        for recipeG in recipeD.findAll("li"):
                            description = description + recipeG.text.strip()
                        recipeDescription = description

                    recipeIdList.append(i + 1)
                    if not recipeName:
                        continue
                    elif not recipeType:
                        continue
                    elif not recipeCount:
                        continue
                    elif not recipePreparationTime:
                        continue
                    elif not recipeCookingTime:
                        continue
                    elif not recipeDescription:
                        continue
                    else:
                        recipeNameList.append(recipeName)
                        recipeTypeList.append(recipeType)
                        recipeMaterialList.append(materialList.copy())
                        recipeMaterialIdList.append(materialIdList.copy())
                        materialList.clear()
                        materialIdList.clear()
                        recipeCountList.append(recipeCount)
                        recipePreparationTimeList.append(recipePreparationTime)
                        recipeCookingTimeList.append(recipeCookingTime)
                        recipeRecipeList.append(recipeDescription)
                        recipeId = ''
                        recipeName = ''
                        recipeType = ''
                        recipeMaterial = ''
                        recipeCount = ''
                        recipePreparationTime = ''
                        recipeCookingTime = ''
                        recipeDescription = ''
                        print(i+1)
            data={'recipeID':recipeIdList,'recipeName':recipeNameList,'recipeType':recipeTypeList,'recipeMaterialId':recipeMaterialIdList,'recipeMaterial'
                :recipeMaterialList,
                'recipeCount':recipeCountList,'recipePrepartion':recipePreparationTimeList,'recipeCooking':recipeCookingTimeList,
                'recipeDescription':recipeRecipeList}
            with open("Yemek.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = list(data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for values in zip(*data.values()):
                    row = {k: v for k, v in zip(data.keys(), values)}
                    writer.writerow(row)
                print("Veri çekme işlemi sonlandı. Bulunan kayıt sayısı: " + str(len(recipeIdList)))
            with open("Direct.txt", "w",encoding="utf-8-sig") as f:
                for r in dataMaterialList:
                    f.write(r+"\n")
                sys.exit()