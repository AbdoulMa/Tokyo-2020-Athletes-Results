## TOKYO Olympics Games Athletes & Results

This repository is an attempt to give an answer to a [Professor Rob J Hyndman request.](https://twitter.com/robjhyndman/status/1424674757044170754)

![](rob_j_hyndman.png)

## How Data is retrievied ?


I scrape the data from official [Olympics Website](https://olympics.com) using `Selenium Driver` with `Python` and [rvest library](https://github.com/tidyverse/rvest) with `R`.

### Why `Selenium Driver` and so `Python` ? 

For the simple reason  that  I need interactively with th browser (click on the `next` button) for go to  the athletes list Page 1 to Page 2 and so on till Page 583. 
On each page, I retrieve the athletes `name`, `country`, `discipline` and the more important the `links` to their results & events page.

The script is in  <a href="retrieve_olympic_athletes.py">retrieve_olympic_athletes.py</a> file.

### Why `rvest` and so `R` ? 

Because the simple reason that  I tried to scrape  players results with `Python` but  I wans't able to do 
the iteration for all the **11656 athletes** efficiently with the methods that `webdriver` or `request` packages. 

So, I used `rvest` which is more than an alternative and `purrr` library  methods to do the iterations efficently.

You can find the complete  script <a href="scrape_athletes_results.R">here</a>.

Last updated on 08/10/2021.
