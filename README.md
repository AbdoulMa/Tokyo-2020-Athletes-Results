## TOKYO Olympics Games Athletes & Results

This repository is an attempt to give an answer to a [Professor Rob J Hyndman question.](https://twitter.com/robjhyndman/status/1424674757044170754)

![](rob_j_hyndman.png)

## How Data are retrieved?

I scrape the data from official [Olympics Website](https://olympics.com) using `Selenium Webdriver` with `Python` and [rvest library](https://github.com/tidyverse/rvest) with `R`.

### Why `Selenium Webdriver` and so `Python`? 

For the simple reason  that  I need to interact with th browser (click on the `next` button) for go to  the athletes list Page 1 to Page 2 and so on, till Page 583. 
On each page, I retrieve the athletes `names`, `countries`, `disciplines` and the more important, the `links` to their results & events pages.

The script is in  <a href="retrieve_olympic_athletes.py">retrieve_olympic_athletes.py</a> file.

### Why `rvest` and so `R` ? 

I tried to scrape  athletes results with `Python` but  I wasn't able to do 
the iteration for all the **11656 athletes** efficiently with the methods that `webdriver` or `requests` packages provide. 

So, I used `rvest` which is more than an alternative and `purrr` library  methods to do the iterations efficiently.

You can find the complete  script <a href="scrape_athletes_results.R">here</a>.

## Informations retrieved 

For each athlete, I scrape (if provided) his/her: 

- name
- country
- birth date 
- discipline (example : Judo, Rowing .. etc ) 
- age 
- gender 
- height in meter 
- height in feet 
- birth place 
- birth country 
- residence place 
- residence country 
- event name (example : Women - 63 Kg, Mixed Team, Men's Double Sculls ... etc )
- event rank 
- event medal 

Last updated on 08/15/2021.
