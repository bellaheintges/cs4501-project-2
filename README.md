## CS4501 Project 2
### Group Members: Bella Heintges, Emmie Halter, Ryan Steele
# Inferring Location History from Online Data

## Overview
This repository contains the code and methodology used to analyze personal location history data extracted from Snapchat’s Location Timeline feature. The goal of this project is to infer “significant locations” based on GPS traces and app usage patterns, revealing places of importance such as home, school, or frequent social spots.

Using Python, clustering algorithms, and the Foursquare Places API, we transform raw location data into meaningful geographic and behavioral insights.

## Data Collection
- Location data was exported from Snapchat via its data request tool.
- The data format was JSON, containing GPS coordinates and timestamps.
- The dataset only included moments when Snapchat was actively in use, leading to sparsity and behavioral skew.

## Methodology
1. Parsing & Cleaning: Python scripts were developed to extract, clean, and format the JSON data, filtering out GPS noise and converting timestamps.
2. Clustering Significant Locations: The DBSCAN algorithm (with haversine distance) was applied to group GPS points into meaningful clusters. This helped distinguish between transition points and actual visited locations.
3. Location Labeling with Foursquare API: The Foursquare Places API was used to enrich clusters with venue names and categories. Categories were assigned to each location cluster.

## Repository Contents
