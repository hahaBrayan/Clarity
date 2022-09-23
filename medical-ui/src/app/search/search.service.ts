import { Injectable } from '@angular/core';
import {
  HttpClient, HttpParams
} from "@angular/common/http";
import { SearchVM } from './SearchVM.model';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  constructor(private http: HttpClient) { }

  searchTerm(searchVM: SearchVM) {
    let params = new HttpParams();
    console.log(searchVM);
    params = params.append('name', searchVM.name);
    params = params.append('form', searchVM.form);
    params = params.append('dosage', searchVM.dosage.toString() + searchVM.dosageUnits);
    params = params.append('zip_code', searchVM.zipCode);
    params = params.append('quantity', searchVM.quantity.toString());
    params = params.append('is_generic', searchVM.isGeneric);
    params = params.append('buyer_price', searchVM.buyerPrice.toString());
    return this.http.get('/api/search', {params: params});
  }

  bulkSearch(formData: FormData) {
    return this.http.post('/api/search/bulk', formData);
  }
}
