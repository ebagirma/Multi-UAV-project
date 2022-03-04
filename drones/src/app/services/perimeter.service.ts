import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

const BASE_URL = 'http://localhost:5000/'

@Injectable({
  providedIn: 'root'
})
export class PerimeterService {

  constructor(private http: HttpClient) { }

  getPerimeter(farmId) {
    return this.http.get(`${BASE_URL}get/locations/${farmId}/`);
  }

  getDrones(farmId) {
    return this.http.get(`${BASE_URL}get/drones/${farmId}/`);
  }

  getPictures(farmId) {
    return this.http.get(`${BASE_URL}get/pictures/${farmId}/`);
  }

  setPerimeter(perimeter, farmId) {
    return this.http.post(`${BASE_URL}set/locations/`, {farm_id: farmId, locations: perimeter[0]});
  }

  updateSchedule(lps, droneId) {
    return this.http.post(`${BASE_URL}update/schedule/${droneId}/`, {lps});
  }

  getFarms() {
    return this.http.get(`${BASE_URL}farms/`);
  }

  getParameters(farm) {
    return this.http.get(`${BASE_URL}get/sps/${farm}/`);
  }

  saveParameters(obj) {
    return this.http.post(`${BASE_URL}set/sps/`, obj);
  }

  getFarmDetail(id) {
    return this.http.get(`${BASE_URL}farms/${id}/` );
  }

  createFarm(param: { city: any; name: any; description: any }) {
    return this.http.post(`${BASE_URL}create/farm/`, param);
  }

  scanDrones(farm) {
    return this.http.get(`${BASE_URL}scan/${farm}/`);
  }

  surveyPlan(farm) {
    return this.http.get(`${BASE_URL}start/${farm}/`);
  }

}
