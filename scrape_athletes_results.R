# Load libraries ----------------------------------------------------------
library(tidyverse)
library(rvest)
library(textclean) # https://rdrr.io/cran/textclean/f/README.md
library(textme)

# Read Data previously scraped --------------------------------------------
athletes <- read_csv("athletes.csv")


scrape_athete_resullts <- function(name, country, discipline, link) {
  athlete_page <- link %>%
    read_html()
  birth_date = ""
  age = ""
  gender = ""
  height = ""
  birth_place = ""
  birth_country = ""
  residence_place = ""
  residence_country = ""
  
  athlete_infos <-  athlete_page %>% 
    html_element("div.row:nth-child(3)") %>% 
    html_elements("div") %>% 
    html_elements("div") %>% 
    html_text2() %>% 
    replace_white()
  athlete_infos
  
  for (info in athlete_infos) {
    if (str_detect(info," Date of Birth: ")) birth_date = str_remove(info," Date of Birth: ") 
    else if (str_detect(info," Age: ")) age = str_remove(info," Age: ") 
    else if (str_detect(info," Gender: ")) gender = str_remove(info," Gender: ") 
    else if (str_detect(info," Height \\(m/ft\\): ")) height = str_remove(info," Height \\(m/ft\\): ") 
    else if (str_detect(info," Place of birth: ")) birth_place = str_remove(info," Place of birth: ") 
    else if (str_detect(info," Birth Country: ")) birth_country = str_remove(info," Birth Country: ") 
    else if (str_detect(info," Place of residence : ")) residence_place = str_remove(info," Place of residence : ") 
    else if (str_detect(info," Residence Country: ")) residence_country = str_remove(info," Residence Country: ") 
  }
  
  nodes <- athlete_page %>% 
    html_element(".table-schedule") %>% 
    html_elements("tr") 
  
  nodes <- nodes[-1] # Remove headers 
  
  # Function to retrieve athlete results
  get_event_results <- function(row) {
    event_name = ""
    event_rank = ""
    event_medal = ""
    event_cells <- row %>% 
      html_elements("td")
    
    event_name <- event_cells[2] %>% 
      html_element("a") %>% 
      html_text()
    
    event_rank <- event_cells[3] %>% 
      html_text2()  %>% 
      replace_white()  %>% # remove escape 
      str_remove_all(" ")
    
    event_medal <- event_cells[4] %>% 
      html_element("img") %>% 
      html_attr("title") %>% 
      str_replace(" Medal","")
    
    tibble(
      name, 
      country,
      birth_date,
      discipline,
      age,
      gender,
      height,
      birth_place,
      birth_country,
      residence_place,
      residence_country, 
      event_name,
      event_rank,
      event_medal
    ) %>% 
      extract(col = height, "(.*)/(.*)", into = c("height_in_m","height_in_feet"))
  }
  
  map_df(nodes, get_event_results)
}

athletes_results <- athletes %>% 
    pmap_df(scrape_athete_resullts)


write_csv(athletes_results, "athletes_results.csv")
textme(message = paste(emo::ji("smile")," Scraping completed !"))


