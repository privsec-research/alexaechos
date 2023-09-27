'use strict';

import * as readline from 'node:readline';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import {stdin, stdout} from 'process';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import AdblockerPlugin from 'puppeteer-extra-plugin-adblocker';

const fileExists = async path => !!(await fsPromises.stat(path).catch(_ => false));

async function isErrorPage(page) {
    return page.evaluate(() => {
      if (document.body.textContent.includes('Something went wrong on our end.')) return true;
      if (document.title.includes('Sorry! Something went wrong!')) return true;
      return false;
    });
}

async function gotoAmazonPage(page, url, rl) {
  while (true) {
    try {
      await page.goto(url);
    } catch (error) {
      console.error(error);
      continue;
    }

    if (await isErrorPage(page)) {
      console.log("Something went wrong!!! Retrying...");
      await page.cookies().then(cookies => page.deleteCookie(...cookies));
      await page.waitForTimeout(2000);
      continue;
    }

    if (null === await page.$('#captchacharacters')) {
      break;
    } else {
      await page.screenshot({ path: 'page.png' });

      const answer = await new Promise(resolve => {
        rl.question('Captcha: ', resolve);
      });

      await page.type('#captchacharacters', answer);
      await page.click('button[type=submit]');
      await page.waitForTimeout(2000);
    }
  }
}



(async () => {
  const groupedSkills = await fsPromises.readFile('subgrouped_skills.json').then(JSON.parse);

  puppeteer.use(StealthPlugin());
  puppeteer.use(AdblockerPlugin({ blockTrackers: true }))

  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({width: 1080, height: 1920});

  const rl = readline.createInterface({input: stdin, output: stdout});

  const categories = ["Religion-Spirituality", "SmartHome", "Health-Fitness", "Navigation-TripPlanners",
                      "Pets-Animals", "Wine-Beverages", "Fashion-Style", "ConnectedCar", "Dating"];
  await fsPromises.mkdir("top50-skill-pages", { recursive: true });

  for (const cat of categories) {
    const top50 = Object.entries(groupedSkills[cat])
                        .map(x => [x[0], x[1].Total_customer_that_rate_the_skill])
                        .sort((a, b) => b[1] - a[1])
                        .slice(0,50)
                        .map(x => x[0]);
    for (const id of top50) {
      const url = `https://www.amazon.com/dp/${id}/`;
      const outputPath = path.join(`top50-skill-pages/${id}.html`);

      if (await fileExists(outputPath)) {
        console.log(`Skip ${id} ...`);
        continue;
      }

      console.log(`Visiting ${url} ...`);
      await gotoAmazonPage(page, url, rl);
      await page.waitForTimeout(1000);

      const content = await page.content();
      await fsPromises.writeFile(outputPath, content);
    }
  }

  await browser.close();
  rl.close();
})();
