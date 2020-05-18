try:
	import urllib.request as urllib2
except ImportError:
	import urllib2

import sys  
import re
import json
import csv
import codecs
import os
import socket
import argparse
from socket import AF_INET, SOCK_DGRAM
from importlib import reload

import requests
from bs4 import BeautifulSoup

from collections import Counter


class LyricScraper:
	"""Lyric Scraper class"""
	def __init__(self, credentials_file, output_file):
		self.credentials_file = credentials_file
		self.output_file = output_file
		with open(self.credentials_file, "r") as inf:
			settings = json.loads(inf.read())
		self.client_access_token=settings["client_access_token"]
		self.client_secret=settings["client_secret"]
		self.client_id=settings["client_id"]

	def get_artist_id(self,search_term,num_pages=25):
		# get_artist_id
		# method to check first num_pages of results for a 
		# search query and finds the most common artist id
		mycounter = Counter()
		for i in range(num_pages):
			querystring = "http://api.genius.com/search?q=" + urllib2.quote(search_term) + "&page=" + str(i+1)
			request = urllib2.Request(querystring)
			request.add_header("Authorization", "Bearer " + self.client_access_token)  
			#Must include user agent of some sort, otherwise 403 returned 
			request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)") 

			while True:
				try:
					#timeout set to 4 seconds; automatically retries if times out
					response = urllib2.urlopen(request, timeout=4) 

					raw = response.read()
				except socket.timeout:
					print("Timeout raised and caught")
					continue
				break
			json_obj = json.loads(raw)
			body = json_obj["response"]["hits"]
			num_hits = len(body)
			if num_hits==0:
				if i==0:
					print("No results for: " + search_term)
				break
			for result in body:
				primaryartist_id = result["result"]["primary_artist"]["id"]
				primaryartist_name = result["result"]["primary_artist"]["name"]
				primaryartist_url = result["result"]["primary_artist"]["url"]
				if primaryartist_name.lower() == search_term.lower() :
					mycounter[primaryartist_id]+=1
		artist_id=mycounter.most_common()
		return artist_id[0][0]


	def get_artists_songs(self,artists_id):
		# get_artists_songs
		# method to get a list of api paths for all the songs of 
		# a given artists_id	
		api_paths=[]
		querystring = "http://api.genius.com/artists/" + urllib2.quote(str(artists_id)) + "/songs"
		request = urllib2.Request(querystring)
		request.add_header("Authorization", "Bearer " + self.client_access_token)   
		#Must include user agent of some sort, otherwise 403 returned
		request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)") 

		try:
			#timeout set to 4 seconds; automatically retries if times out
			response = urllib2.urlopen(request, timeout=4) 

			raw = response.read()
		except socket.timeout:
			print("Timeout raised and caught")
			return None
		json_obj = json.loads(raw)
		body = json_obj["response"]["songs"]
		num_hits = len(body)
		if num_hits==0:
			if page==1:
				print("No results for: " + search_term)
				return None
		for result in body:
			api_paths.append(result['api_path'])
		return api_paths


	def get_lyrics(self,api_paths):
		# get_lyrics
		# method to get a list of lyrics in txt from a 
		# given list of api_paths	
		base_url = "http://api.genius.com"
		lyrics=[]
		for song in api_paths:
			song_url = base_url + song
			request = urllib2.Request(song_url)
			request.add_header("Authorization", "Bearer " + self.client_access_token) 
			#Must include user agent of some sort, otherwise 403 returned  
			request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)") 

			try:
				response = urllib2.urlopen(request, timeout=4)
				raw = response.read()
			except socket.timeout:
				print("Timeout raised and caught")
			else:
				json_obj = json.loads(raw)
				path = json_obj["response"]["song"]["path"]
				page_url = "http://genius.com" + path
				page = requests.get(page_url).text
				html = BeautifulSoup(page, "html.parser")
				[h.extract() for h in html('script')]
				new_lyrics = html.find("div", class_="lyrics")
				if new_lyrics is not None:
					nlyrics = new_lyrics.get_text()
					#print(new_lyrics)
					lyrics.append(nlyrics)

		return lyrics

	def write_lyrics(self,lyrics):
		# write_lyrics
		# method to write the list of lyrics to a txt file
		output_file = open(self.output_file, 'w', encoding='utf8')
		for song in lyrics:
			output_file.write("%s\n" % song)
		output_file.close()

def main():
	# fetch args
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--credentials', help='Path to the credentials file')
	parser.add_argument('-a', '--artist', help='Name of the artist')
	parser.add_argument('-o', '--output', help='Path to the outputfile')
	args = parser.parse_args()

	myScraper=LyricScraper(args.credentials,args.output)
	artist_id=myScraper.get_artist_id(args.artist)
	api_paths=myScraper.get_artists_songs(artist_id)
	lyrics=myScraper.get_lyrics(api_paths)
	myScraper.write_lyrics(lyrics),


if __name__ == '__main__':
	main()