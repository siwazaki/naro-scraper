import sys
import os
import time
import re
from urllib import request
from bs4 import BeautifulSoup

import hydra
from tqdm import tqdm
from loguru import logger


def get_nb_parts(ncode, cfg):
    url = f"{cfg.naro.info_top_url}/{ncode}"
    try:
        res = request.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        pre_info = soup.select_one("#pre_info").text
        return int(re.search(r"全([0-9]+)部分", pre_info).group(1))
    except Exception:
        return None


def scrape_one(ncode, cfg):
    logger.info(f"begin to scrape ncode:{ncode}")
    ncode = ncode.lower()
    if not re.match(r"n[0-9]{4}[a-z]{2}", ncode):
        logger.warning(f"ncode {ncode} is invalid")
        return

    nb_parts = get_nb_parts(ncode, cfg)

    if nb_parts is None:
        logger.warning(f"could _NOT_ get nb_parts of {ncode}")
        return

    logger.info(f"nb_parts:{nb_parts}")

    output_root_dir = cfg.naro.output_root_dir
    novel_dir = os.path.normpath(os.path.join(output_root_dir, ncode))

    if not os.path.exists(novel_dir):
        os.mkdir(novel_dir)

    fetches = range(1, nb_parts + 1)
    for part in tqdm(fetches):
        try:
            url = f"{cfg.naro.top_url}/{ncode}/{part}/"
            res = request.urlopen(url)
            soup = BeautifulSoup(res, "html.parser")
            content = soup.select_one("#novel_honbun").text
            path = os.path.join(novel_dir, f"{ncode}-{part}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            logger.error("failed")
            pass

        time.sleep(1)


def read_target_file(path):
    with open(path) as f:
        return f.readlines()


@hydra.main(config_name='config')
def main(cfg):
    output_root_dir = cfg.naro.output_root_dir
    logfile = cfg.naro.logfile
    logger.add(logfile)
    if not os.path.exists(output_root_dir):
        os.mkdir(output_root_dir)

    ncodes = read_target_file(cfg.naro.target_file)
    for ncode in tqdm(ncodes):
        ncode = ncode.strip()
        scrape_one(ncode, cfg)


if __name__ == "__main__":
    main()
