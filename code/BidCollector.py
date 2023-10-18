import traceback
import json
import time
import os


class BidCollector():
	
	def __init__(self, profile, site, tranco_rank, bid_output_path) -> None:
		self.profile = profile
		self.tranco_rank = tranco_rank
		self.site = site
		self.bid_output_filepath = bid_output_path

	def saveBids(self, bids, logger):
		current_time = time.time()
		with open(self.bid_output_filepath, 'w') as out_file:
			for item in bids:
				out_file.write(json.dumps(item)) 
				out_file.write('\n')
		out_file.close()
		logger.write("\nBids written to a file for domain: {} [Time: {}]".format(self.site, self.profile, time.time()-current_time))
		return

	def collectBids(self, webdriver, logger):
		current_time = time.time()
		bid_start_time = current_time
		GET_CPM = """var output = [];
					 function getCPM()
					 {	 
						 var responses = pbjs.getBidResponses();
						 var winners = pbjs.getAllWinningBids();
						 Object.keys(responses).forEach(function(adUnitCode) {
						 var response = responses[adUnitCode];
							 response.bids.forEach(function(bid)
							 {
								 output.push({
								 bid: bid,
								 adunit: adUnitCode,
								 adId: bid.adId,
								 bidder: bid.bidder,
								 time: bid.timeToRespond,
								 cpm: bid.cpm,
								 msg: bid.statusMessage,
								 rendered: !!winners.find(function(winner) {
									 return winner.adId==bid.adId;
								 })
								 });
							 });
						 });
					 }
					 getCPM();
					 return output;
				 """

		GET_FORCED_CPM = """window.updated_output = [];
							function sendAdserverRequest(responses, timeout) {
								Object.keys(responses).forEach(function(adUnitCode) {
									var response = responses[adUnitCode];
										response.bids.forEach(function(bid) 
										{
											window.updated_output.push({
											bid: bid,
											adunit: adUnitCode,
											adId: bid.adId,
											bidder: bid.bidder,
											time: bid.timeToRespond,
											cpm: bid.cpm,
											msg: bid.statusMessage,
											});
										});
									});
							}

							pbjs.requestBids({
								bidsBackHandler: sendAdserverRequest,
								timeout: 1000
							});
						"""
		GET_FORCED_CPM_RETURN = "return window.updated_output;"

		bids = []
		try:
			bids = webdriver.execute_script(GET_CPM) # These are the NORMAL Bids
			method = "NORMAL"
			logger.write("\nNORMAL Bids extracted for domain: {} [Time: {}]".format(self.site, self.profile, time.time()-current_time))
			if len(bids) == 0:
				webdriver.execute_script(GET_FORCED_CPM)
				time.sleep(5)
				bids = webdriver.execute_script(GET_FORCED_CPM_RETURN)
				method = "FORCED" # These are the FORCED Bids
				logger.write("\nFORCED Bids extracted for domain: {} [Time: {}]".format(self.site, self.profile, time.time()-current_time))
			if len(bids) > 0:
				# print(self.tranco_rank, self.site, "True")
				self.bid_output_filepath = str(self.bid_output_filepath).replace("-bids", "-{}-bids".format(method))
				self.saveBids(bids, logger)
				logger.write("\nNORMAL Bids extracted for domain: {} [Time: {}]".format(self.site, self.profile, time.time()-current_time))
			else:
				# print(self.tranco_rank, self.site, "False")
				pass
		except Exception as e:
			current_time = time.time()
			try:
				webdriver.execute_script(GET_FORCED_CPM)
				time.sleep(5)
				bids = webdriver.execute_script(GET_FORCED_CPM_RETURN)
				method = "FORCED" # These are the FORCED Bids
				logger.write("\nFORCED Bids extracted for domain: {} [Time: {}]".format(self.site, self.profile, time.time()-current_time))
				if len(bids) > 0:
					# print(self.tranco_rank, self.site, "True")
					self.bid_output_filepath = str(self.bid_output_filepath).replace("-bids", "-{}-bids".format(method))
					self.saveBids(bids, logger)
					logger.write("\nNORMAL Bids extracted for domain: {} [Time: {}]".format(self.site, self.profile, time.time()-current_time))
				else:
					# print(self.tranco_rank, self.site, "False")
					pass
			except:
				logger.write("\n[ERROR] collectBids()::BidCollector: {}\nException occured in bid collection for domain: {} | {} [Time: {}]".format(str(traceback.format_exc()), self.site, self.profile, time.time()-current_time))
				# print('EXCEPTION occured in bid collection:', str(e))
				return

		# print("Collected bids on {}".format(self.site))
		logger.write("\nBid collection successfully completed for domain: {} | {} [Time: {}]".format(self.site, self.profile, time.time()-bid_start_time))
		return
