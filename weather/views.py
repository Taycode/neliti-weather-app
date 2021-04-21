from django.shortcuts import render
from django.views import View
import requests
from django.conf import settings


def clean_symbol_code(code):
	"""Cleans Weather Symbol code"""
	sentence = code.split('_')
	return (' '.join(sentence)).capitalize()


def get_weather(longitude, latitude):
	"""Gets longitude and latitude"""
	url = 'https://api.met.no/weatherapi/locationforecast/2.0/compact'
	params = {
		'lon': longitude,
		'lat': latitude
	}
	headers = {
		'User-Agent': 'TayCode'
	}
	response = requests.get(url, params=params, headers=headers).json()
	weather_data = response.get('properties').get('timeseries')[0]
	weather_data = weather_data.get('data')
	return {
		'next_hour': clean_symbol_code(weather_data.get('next_1_hours').get('summary').get('symbol_code')),
		'next_6_hours': clean_symbol_code(weather_data.get('next_6_hours').get('summary').get('symbol_code')),
		'next_12_hours': clean_symbol_code(weather_data.get('next_12_hours').get('summary').get('symbol_code')),
	}


def get_coordinates_from_location(location):
	"""Gets coordinates from location"""
	url = 'https://api.opencagedata.com/geocode/v1/json'
	params = {
		'key': settings.OPENCAGE_API_KEY,
		'q': location
	}
	response = requests.get(url, params=params).json()
	results = response.get('results')
	if not results:
		return None
	result = results[0]
	geometry = result.get('geometry')
	return {
		'latitude': geometry.get('lat'),
		'longitude': geometry.get('lng')
	}


class HomepageView(View):
	"""Home page view"""

	def get(self, request):
		"""Get Method"""
		location = request.GET.get('location')
		lat_and_long = get_coordinates_from_location(location)
		context = dict()
		if lat_and_long:
			latitude, longitude = (lat_and_long.get('latitude'), lat_and_long.get('longitude'))
			weather = get_weather(longitude, latitude)
			context.update(weather)
			context.update({'weather': True})
		return render(request, 'weather/homepage.html', context)
