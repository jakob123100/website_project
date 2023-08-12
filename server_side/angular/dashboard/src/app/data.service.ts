import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  baseURL = 'http://217.208.66.120:7777';

  constructor(private http: HttpClient) {}

  getLatestData(site: string, category: string) {
    return this.http.get(`${this.baseURL}/${site}/${category}/get/latest`);
  }
}