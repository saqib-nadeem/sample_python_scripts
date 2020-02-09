#--------------------------------------
#History
#06.20.2015: Saqib: Update logging system, Replaced systemExit, Standardized the indentation to four spaces,added functions names as comments, 
#added condition for creating crawler object,removed redundant comments and spaces, Added support for fetching sale items only
#--------------------------------------

from lxml.cssselect import CSSSelector
from urlparse import urlparse
import httplib2
import sys
import Queue
import itertools
import argparse

import common
reload(common)
from common import crawlerCommon

#---------------------------------
# Crawler config params for Ssense

class SsenseConfig(crawlerCommon.CommonConfig):

    def __init__(self, _sale):
        self.swl = crawlerCommon.SWLLogger('Ssense', 'debug', True, 'debug')
        self.sale_items_only = _sale

    ############################
    #fetchCategories
    ############################  
    def FetchCategories(self,
                        page_url,
                        mapping_list,
                        css_selector,
                        sex):

        h = crawlerCommon.NetworkIOManager.read_link(page_url, None)
        anchor_tags_in_submenu = css_selector(h)
        anchors_list = []

        for item in anchor_tags_in_submenu:
            if isinstance(item.text, str):
                anchor_text = item.text.strip().rstrip()
                #self.swl.logdebug (anchor_text);
                anchor_url = item.get("href")
                anchors_list.append({"anchor_text":anchor_text,
                                     "anchor_url": anchor_url})

        found_items_counter = 0;
        list_items_found = []
        for anchor in anchors_list:
            for k, v in mapping_list.iteritems():
                titles_only = []

                for entry in v:
                    titles_only.append(entry["title"])

                if anchor["anchor_text"] in titles_only:
                    subcategory = ""

                    for e in v:
                        if e["title"] == anchor["anchor_text"]:
                            subcategory = e["subcategory"]

                    self.swl.logdebug("Found *" + k + "* for " + anchor["anchor_text"])
                            
                    self.categoriesQ.put({"sex":sex,
                                 "category_url": anchor["anchor_url"],
                                 "category_title":k,
                                 "subcategory": subcategory
                                })

                    list_items_found.append(anchor["anchor_text"])
                    found_items_counter += 1
                    break

        total_items_to_find = 0
        list_items_to_find = []

        for k, v in mapping_list.iteritems():
            total_items_to_find += len(v)
            list_items_to_find.append(v)

        list_items_to_find = list(itertools.chain(*list_items_to_find))
        self.swl.loginfo("Found " + str(found_items_counter) + "/" + str(total_items_to_find) + " items")

        if (found_items_counter != total_items_to_find):
            self.swl.logcritical("Category items missing")
            self.swl.logdebug("page_url = " + page_url)
            #self.swl.logcritical("list_items_to_find = " + str(list_items_to_find))
            #self.swl.logcritical("list_items_found = "+ str(list_items_found))
            raise crawlerCommon.SwlException(crawlerCommon.CATEGORIES_MISMATCH)

        self.swl.loginfo("")
    
    total_pages = 0
    ############################
    #findTotalPages
    ############################ 
    css_selector_string_for_total_pages = CSSSelector("div.numbers > a:last-child")
    def findTotalPages(self, h):
        if h == None:
            return 1

        temp = self.css_selector_string_for_total_pages(h)

        if len(temp) == 0:
            self.total_pages = 1
            return 1
        else:
            total_pages = temp[0].text
            self.total_pages = total_pages
            return total_pages
 
    ############################
    #fetchItemsQueue
    ############################
    css_selector_string_for_item_box = CSSSelector("ul#productList li.cp_item")
    def fetchItemsQueue(self, h):
        items_boxes_list = self.css_selector_string_for_item_box(h)
        return items_boxes_list

    ############################
    #findNextPageUrl
    ############################
    css_selector_string_for_next_page = CSSSelector("nav#cp_pages #nextPg")
    def findNextPageUrl(self, h, current_page_number):
        temp = self.css_selector_string_for_next_page(h)
        next_page = None

        if len(temp) == 0:
            next_page = None
        else:
            next_page = temp[0].get("href")

        return next_page
    
    ############################
    #fetchItemURL
    ############################
    css_selector_string_for_item_url = CSSSelector("a")
    def fetchItemURL(self, h):
        temp = self.css_selector_string_for_item_url(h)

        if len(temp) == 0:
            return "?"
        else:
            item_path = temp[0].get("href")
            o = urlparse(item_path)
            item_path = o.path
            item_url = self.server_root + item_path
            return item_url
    
    ############################
    #fetchItemImageURL
    ############################
    css_selector_string_for_item_small_image_url = CSSSelector("meta[property='og:image']")
    def fetchItemImageURL(self, h):
        small_image_url_element = self.css_selector_string_for_item_small_image_url(h)

        if (len(small_image_url_element) > 0):
            item_image_url_orig = small_image_url_element[0].get("content")
            item_image_url = item_image_url_orig.replace("/02/2/3/", "/02/2/1/")
            item_image_url = item_image_url.replace("/02/1/3/", "/02/1/1/")
            item_image_url = item_image_url.replace("/01/2/3/", "/01/2/1/")
            item_image_url = item_image_url.replace("/00/2/3/", "/00/2/1/")
            item_image_url = item_image_url.replace("/00/2/3/", "/00/2/1/")
            item_image_url = item_image_url.replace("/01/1/3/", "/01/1/1/")
            item_image_url = item_image_url.replace("/00/1/3/", "/00/1/1/")
            item_image_url = item_image_url.replace("/03/1/3/", "/03/1/1/")
            item_image_url = item_image_url.replace("/03/2/3/", "/03/2/1/")
            large_image_url = item_image_url.replace("_1_3.jpg", "_1_1.jpg")

            if self.nwio.itExists(large_image_url) and self.nwio.itExists2(large_image_url):
               image_url = large_image_url
               return image_url
            else:
                image_url = item_image_url_orig
                self.swl.logerror("Large image not found") 
                return image_url 

        else:
            return "?"
    
    ############################
    #fetchItemBrandTitle
    ############################
    css_selector_string_for_item_brand = CSSSelector("a.pp_m_brand span")
    css_selector_string_for_item_title = CSSSelector("p.name")
    def fetchItemBrandTitle(self, h):
        temp_brand = self.css_selector_string_for_item_brand(h)
        temp_title = self.css_selector_string_for_item_title(h)

        brand_title = {"brand":"?",
                       "title":"?"}

        if (len(temp_brand) == 1):
            brand_name = temp_brand[0].text.strip().lstrip()
            brand_title["brand"] = brand_name.replace(" //","")

        if (len(temp_title) == 1):
            brand_title["title"] = temp_title[0].text.strip().lstrip()

        return brand_title
    
    ############################
    #fetchItemDetails
    ############################
    css_selector_string_for_item_details = CSSSelector("p.desc")
    def fetchItemDetails(self, h):
        temp = self.css_selector_string_for_item_details(h)
        item_details = "?"

        if len(temp) > 0:
            item_details = temp[0].text_content().strip().lstrip()
            return item_details
        else:
            return item_details

    ############################
    #fetchItemPrice
    ############################ 
    css_selector_string_for_item_price_new = CSSSelector("p.price_new")
    css_selector_string_for_item_price_old = CSSSelector("p.price_old")
    def fetchItemPrice(self, item_box):
        price_new = self.css_selector_string_for_item_price_new(item_box)
        price_old = self.css_selector_string_for_item_price_old(item_box)

        price_dict = {"price":"?", "sale_price":""}

        if len(price_old) > 0:
            sale_price = price_new[0].text_content().strip()
            price_dict["sale_price"] = sale_price.replace(" USD","")
            price = price_old[0].text_content().strip()
            price_dict["price"] = price.replace(" USD","")
        elif len(price_new) > 0:
            price = price_new[0].text_content().strip()
            price_dict["price"] = price.replace(" USD","")
                
        return price_dict

    ############################
    #fetchItemInfo
    ############################
    def fetchItemInfo(self, item_box):

        item_url = self.fetchItemURL(item_box)
        h = crawlerCommon.NetworkIOManager.read_link(item_url, None)

        if h == None:
            self.swl.logwarn("Could not locate item - skipping")
            return None

        item_image_url = self.fetchItemImageURL(h)
        item_brand_and_title = self.fetchItemBrandTitle(h)
        item_details = self.fetchItemDetails(h)
        item_price_dict = self.fetchItemPrice(h)

        item_info = {"item_url": item_url,
                     "image_url":item_image_url,
                     "brand":item_brand_and_title["brand"],
                     "title":item_brand_and_title["title"],
                     "regular_price":item_price_dict["price"],
                     "sale_price":item_price_dict["sale_price"],
                     "details":item_details
                    }

        return item_info

    ############################
    #PopulateItemsList
    ############################
    def PopulateItemsList(self, items_boxes_list, current_sex, current_category, subcategory):

        item_counter = 0
        total_items = str(len(items_boxes_list))

        for item_box in items_boxes_list:
            self.swl.loginfo(self.sm.PrintLatestStats())
            info_dict = self.fetchItemInfo(item_box)

            if info_dict != None:
                item = {"url":info_dict["item_url"],
                        "image":info_dict["image_url"],
                        "brand":info_dict["brand"],
                        "title":info_dict["title"],
                        "subcategory": subcategory,
                        "price":info_dict["regular_price"],
                        "sale_price":info_dict["sale_price"],
                        "category":current_category,
                        "sex": current_sex,
                        "details": info_dict["details"]
                        }

                crawlerCommon.DiskIOManager.DumpThisItem(item)

            item_counter += 1
            self.swl.loginfo("Fetched item # " + str(item_counter) + "/" + total_items)

    ############################
    #crawl
    ############################
    def crawl(self):
        sys.stdout.write("[")

        for sex in self.swllist["sex"]:
            self.swl.logdebug (sex["title"])
            categories_list = sex["categories"]

            for category in categories_list:
                category_page_url = category["page_url"]
                category_mapping_list = category["mapping"]
                css_selector = category["css_selector"]

                if self.sale_items_only == True:
                    if category["listing_type"] == "sale":
                        self.swl.loginfo(category_page_url)
                        self.FetchCategories(category_page_url, category_mapping_list, css_selector, sex["title"])
                else:
                    self.swl.loginfo(category_page_url) 
                    self.FetchCategories(category_page_url, category_mapping_list, css_selector, sex["title"])

            category_count = str(self.categoriesQ.qsize())
            self.swl.loginfo("category_count = " + category_count)

        for i in range(self.categoriesQ.qsize()):
            now_category = i+1
            current_page = 1

            self.swl.loginfo("NOW ON CATEGORY " + str(now_category))
            
            category = self.categoriesQ[i]
            next_page = category["category_url"]
            category_title = category["category_title"]
            category_sex = category["sex"]
            subcategory = category["subcategory"]

            self.swl.logdebug("Reading - next_page = " + next_page)
            h = self.nwio.read_link(next_page, self.server_root)

            if h == None:
                self.swl.logwarn("Could not locate category - skipping")
                continue

            total_pages = self.findTotalPages(h)
            self.swl.loginfo("total_pages = " + str(total_pages))

            item_boxes_list = self.fetchItemsQueue(h)

            number_of_items_per_page = len(item_boxes_list)
            self.swl.loginfo("len(item_boxes_list) = " + str(number_of_items_per_page))

            self.sm.SetLatestStats(now_category, category_count, str(current_page), total_pages)
            self.swl.loginfo(self.sm.PrintLatestStats())

            self.PopulateItemsList(item_boxes_list, category_sex, category_title, subcategory)

            next_page = self.findNextPageUrl(h,current_page)
            self.swl.loginfo("next_page = " + str(next_page))

            while next_page != "#" and next_page != None:
                h = self.nwio.read_link(next_page, self.server_root)

                if h == None:
                    self.swl.logwarn("Could not locate page - skipping")
                    continue

                item_boxes_list = self.fetchItemsQueue(h)
                current_page += 1

                self.sm.SetLatestStats(now_category, category_count, current_page, total_pages)
                self.swl.loginfo(self.sm.PrintLatestStats())

                self.PopulateItemsList(item_boxes_list, category_sex, category_title, subcategory)

                next_page = self.findNextPageUrl(h,current_page)
                self.swl.loginfo("next_page = " + str(next_page))
                self.swl.loginfo("-------------------")

        sys.stdout.write("]")

    #women
    category_pages_women = []

    #ssense women
    women_category_mapping_1 = {
                               "Tops":       ({"title":"SHIRTS",
                                               "subcategory":""},
                                              {"title":"SWEATERS",
                                               "subcategory":""},),
                               "Bottoms":    ({"title":"JEANS",
                                               "subcategory":""},
                                              {"title":"PANTS",
                                               "subcategory":""},
                                              {"title":"SHORTS",
                                               "subcategory":""},
                                              {"title":"SKIRTS",
                                               "subcategory":""},),
                               "Outerwear":  ({"title":"OUTERWEAR",
                                               "subcategory":""},), 
                               "Footwear":   ({"title":"BOOTS",
                                               "subcategory":""},
                                              {"title":"FLATS",
                                               "subcategory":""},
                                              {"title":"HEELS",
                                               "subcategory":""},
                                              {"title":"SANDALS",
                                               "subcategory":""},
                                              {"title":"SNEAKERS",
                                               "subcategory":""},),
                               "Accessories":({"title":"BAGS",
                                               "subcategory":""},
                                              {"title":"BELTS AND SUSPENDERS",
                                               "subcategory":""},
                                              {"title":"HATS",
                                               "subcategory":""},
                                              {"title":"JEWELRY",
                                               "subcategory":""},
                                              {"title":"SCARVES",
                                               "subcategory":""},
                                              {"title":"SUNGLASSES",
                                               "subcategory":""},
                                              {"title":"ACCESSORIES",
                                               "subcategory":""},),                                                              
                               "Other":      ({"title":"JUMPSUITS",
                                               "subcategory":""},
                                              {"title":"DRESSES",
                                               "subcategory":""},
                                              {"title":"SWIMWEAR",
                                               "subcategory":""},)
                                }

    category_pages_women.append({
                  "mapping": women_category_mapping_1,
                  "page_url":"http://www.ssense.com/women",
                  "css_selector":CSSSelector("#cp_menu_categories a"),
                  "listing_type":"regular"
                })

    #ssense women-underwear
    women_category_mapping_2 = {
                               "Tops":       ({"title":"BRAS",
                                               "subcategory":""},),
                               "Bottoms":    ({"title":"BRIEFS",
                                               "subcategory":""},
                                              {"title":"THONGS",
                                               "subcategory":""},),
                               "Outerwear":  (),
                               "Footwear":   ({"title":"SOCKS",
                                               "subcategory":""},),                                                        
                               "Accessories":(),
                               "Other":      ()
                                }

    category_pages_women.append({
                  "mapping": women_category_mapping_2,
                  "page_url":"http://www.ssense.com/women/designers/all/underwear",
                  "css_selector":CSSSelector("#cp_menu_categories a"),
                  "listing_type":"regular"
                })

    #ssense women-sale
    women_category_mapping_3 = {
                               "Tops":       ({"title":"SHIRTS",
                                               "subcategory":""},
                                              {"title":"SWEATERS",
                                               "subcategory":""},),
                               "Bottoms":    ({"title":"JEANS",
                                               "subcategory":""},
                                              {"title":"PANTS",
                                               "subcategory":""},
                                              {"title":"SHORTS",
                                               "subcategory":""},
                                              {"title":"SKIRTS",
                                               "subcategory":""},),
                               "Outerwear":  ({"title":"OUTERWEAR",
                                               "subcategory":""},), 
                               "Footwear":   ({"title":"BOOTS",
                                               "subcategory":""},
                                              {"title":"FLATS",
                                               "subcategory":""},
                                              {"title":"HEELS",
                                               "subcategory":""},
                                              {"title":"SANDALS",
                                               "subcategory":""},
                                              {"title":"SNEAKERS",
                                               "subcategory":""},),
                               "Accessories":({"title":"BAGS",
                                               "subcategory":""},
                                              {"title":"BELTS AND SUSPENDERS",
                                               "subcategory":""},
                                              {"title":"HATS",
                                               "subcategory":""},
                                              {"title":"JEWELRY",
                                               "subcategory":""},
                                              {"title":"SCARVES",
                                               "subcategory":""},
                                              {"title":"SUNGLASSES",
                                               "subcategory":""},
                                              {"title":"ACCESSORIES",
                                               "subcategory":""},),                                                              
                               "Other":      ({"title":"JUMPSUITS",
                                               "subcategory":""},
                                              {"title":"DRESSES",
                                               "subcategory":""},
                                              {"title":"SWIMWEAR",
                                               "subcategory":""},)
                                }

    category_pages_women.append({
                  "mapping": women_category_mapping_3,
                  "page_url":"http://www.ssense.com/women/sale",
                  "css_selector":CSSSelector("#cp_menu_categories a"),
                  "listing_type":"sale"
                })

    #ssense women-sale-underwear
    women_category_mapping_4 = {
                               "Tops":       ({"title":"BRAS",
                                               "subcategory":""},),
                               "Bottoms":    ({"title":"BRIEFS",
                                               "subcategory":""},
                                              {"title":"THONGS",
                                               "subcategory":""},),
                               "Outerwear":  (),
                               "Footwear":   ({"title":"SOCKS",
                                               "subcategory":""},),                                                        
                               "Accessories":(),
                               "Other":      ()
                                }

    category_pages_women.append({
                  "mapping": women_category_mapping_4,
                  "page_url":"http://www.ssense.com/women/sale/all/underwear",
                  "css_selector":CSSSelector("#cp_menu_categories a"),
                  "listing_type":"sale"
                })

    
    #men 
    category_pages_men = []

    #ssense men
    men_category_mapping_1 = {
                             "Tops":       ({"title":"SHIRTS",
                                             "subcategory":""},
                                            {"title":"SWEATERS",
                                             "subcategory":""},
                                            {"title":"T-SHIRTS",
                                             "subcategory":""},),                                                    
                             "Bottoms":    ({"title":"JEANS",
                                             "subcategory":""},
                                            {"title":"PANTS",
                                             "subcategory":""},
                                            {"title":"SHORTS",
                                             "subcategory":""},
                                            {"title":"BOXERS",
                                             "subcategory":""},
                                            {"title":"BRIEFS",
                                             "subcategory":""},),                          
                             "Outerwear":  ({"title":"OUTERWEAR",
                                             "subcategory":""},),                                                                       
                             "Footwear":   ({"title":"BOOTS",
                                             "subcategory":""},
                                            {"title":"CASUAL SHOES",
                                             "subcategory":""},
                                            {"title":"SANDALS",
                                             "subcategory":""},
                                            {"title":"SNEAKERS",
                                             "subcategory":""},
                                            {"title":"SOCKS",
                                             "subcategory":""},),                                                                  
                             "Accessories":({"title":"BAGS",
                                             "subcategory":""},
                                            {"title":"BELTS AND SUSPENDERS",
                                             "subcategory":""},
                                            {"title":"GLOVES",
                                             "subcategory":""},
                                            {"title":"HATS",
                                             "subcategory":""},
                                            {"title":"JEWELRY",
                                             "subcategory":""},
                                            {"title":"SCARVES",
                                             "subcategory":""},
                                            {"title":"SUNGLASSES",
                                             "subcategory":""},
                                            {"title":"ACCESSORIES",
                                             "subcategory":""},
                                            {"title":"TIES",
                                             "subcategory":""},),
                             "Other":      ({"title":"SUITS",
                                             "subcategory":""},
                                            {"title":"SWIMWEAR",
                                             "subcategory":""},)
                              }

    category_pages_men.append({
                  "mapping": men_category_mapping_1,
                  "page_url":"http://www.ssense.com/men",
                  "css_selector":CSSSelector("ul#cp_menu_categories a"),
                  "listing_type":"regular"
                })

     #ssense men-sale
    men_category_mapping_2 = {
                             "Tops":       ({"title":"SHIRTS",
                                             "subcategory":""},
                                            {"title":"SWEATERS",
                                             "subcategory":""},
                                            {"title":"T-SHIRTS",
                                             "subcategory":""},),                                                    
                             "Bottoms":    ({"title":"JEANS",
                                             "subcategory":""},
                                            {"title":"PANTS",
                                             "subcategory":""},
                                            {"title":"SHORTS",
                                             "subcategory":""},
                                            {"title":"BOXERS",
                                             "subcategory":""},
                                            {"title":"BRIEFS",
                                             "subcategory":""},),                          
                             "Outerwear":  ({"title":"OUTERWEAR",
                                             "subcategory":""},),                                                                       
                             "Footwear":   ({"title":"BOOTS",
                                             "subcategory":""},
                                            {"title":"CASUAL SHOES",
                                             "subcategory":""},
                                            {"title":"SANDALS",
                                             "subcategory":""},
                                            {"title":"SNEAKERS",
                                             "subcategory":""},
                                            {"title":"SOCKS",
                                             "subcategory":""},),                                                                  
                             "Accessories":({"title":"BAGS",
                                             "subcategory":""},
                                            {"title":"BELTS AND SUSPENDERS",
                                             "subcategory":""},
                                            {"title":"GLOVES",
                                             "subcategory":""},
                                            {"title":"HATS",
                                             "subcategory":""},
                                            {"title":"JEWELRY",
                                             "subcategory":""},
                                            {"title":"SCARVES",
                                             "subcategory":""},
                                            {"title":"SUNGLASSES",
                                             "subcategory":""},
                                            {"title":"ACCESSORIES",
                                             "subcategory":""},
                                            {"title":"TIES",
                                             "subcategory":""},),
                             "Other":      ({"title":"SUITS",
                                             "subcategory":""},
                                            {"title":"SWIMWEAR",
                                             "subcategory":""},)
                                            
                              }

    category_pages_men.append({
                  "mapping": men_category_mapping_2,
                  "page_url":"http://www.ssense.com/men/sale",
                  "css_selector":CSSSelector("ul#cp_menu_categories a"),
                  "listing_type":"sale"
                })

    server_root = "http://www.ssense.com"
    swllist = {
      "root": {"title":"Ssense",
               "url": server_root
               },
      "sex":[ {"title":"women",
               "categories":category_pages_women
              },
              {"title":"men",
               "categories":category_pages_men
              },
            ]
      }

#--------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sale", help="optional argument to crawl only sale items - no option means all categories will be crawled",
                    action="store_true")
                    
    args = parser.parse_args()
    if args.sale:
      print "Fetching sale items only"
   
    b = SsenseConfig(args.sale)
    b.crawl()
