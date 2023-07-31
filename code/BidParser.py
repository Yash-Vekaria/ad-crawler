import json
import csv
import os



class BidParser():

	def __init__(self, crawl_to_analyse):

		self.crawl = crawl_to_analyse

	def read_file(self, bid_filepath):
		
		f = open(bid_filepath, "r")
		file_string = f.read().split("\n")
		return file_string

	def parse_bids(self):

		crawl_dir = os.path.join("..", "output", self.crawl)
		output_dir = os.path.join("..", "output", "bids")
		if not(os.path.exists(output_dir)):
			os.makedirs(output_dir)
		output_filepath = os.path.join(output_dir, "{}_bids.csv".format(self.crawl))
		
		with open(output_filepath, "w") as csvfile:
			csvwriter = csv.writer(csvfile)
			for site_dir in os.listdir(crawl_dir):
				bid_file_path = os.path.join(crawl_dir, site_dir, "{}_bids.json".format(site_dir))
				if not(os.path.exists(bid_file_path)):
					continue
				data = self.read_file(bid_file_path)
				for line in data:
					if line.strip().strip("").strip(" ") == "":
						continue
					bid_data = json.loads(line)
					publisher_domain = str(site_dir)
					ad_id = bid_data.get("adId", "")
					bidder = bid_data.get("bidder", "")
					cpm = bid_data.get("cpm", "")
					bid_currency = bid_data.get("bid", {}).get("currency", "")
					floor_value = bid_data.get("bid", {}).get("floorData", {}).get("floorValue", "")
					advertiser_domain = bid_data.get("bid", {}).get("adserverTargeting", {}).get("hb_adomain", "")
					advertiser_id = bid_data.get("bid", {}).get("meta", {}).get("advertiserId", "")
					ad_size = bid_data.get("bid", {}).get("adserverTargeting", {}).get("hb_size", "")
					auction_id = bid_data.get("bid", {}).get("auctionId", "")
					creative_id = bid_data.get("bid", {}).get("creativeId", "")
					deal_id = bid_data.get("bid", {}).get("dealId", "")
					row = [self.crawl, publisher_domain, ad_id, ad_size, creative_id, auction_id, deal_id, bidder, cpm, floor_value, bid_currency, advertiser_id, advertiser_domain]
					print(row)
					csvwriter.writerow(row)
			csvfile.close()
		return



def main():

	profile_to_analyse = "Test"
	bp = BidParser(profile_to_analyse)
	bp.parse_bids()
	return



if __name__ == '__main__':
	
	main()