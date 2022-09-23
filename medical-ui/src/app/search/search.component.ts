import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { SearchService } from './search.service';
import { SearchVM } from './SearchVM.model';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.sass']
})
export class SearchComponent implements OnInit {

  public searchResults: any;
  public medicationForms = ['Tablet', 'Pill', 'Bottle', 'Punchcard', 'Disp Pack'];
  public units = ['mg', 'ml'];
  public searchForm = new FormGroup({
    name: new FormControl('', [Validators.required]),
    medForm: new FormControl('tablet', [Validators.required]),
    dosage: new FormControl(null, [Validators.required]),
    dosageUnits: new FormControl('mg', [Validators.required]),
    zipCode: new FormControl('', [Validators.required]),
    quantity: new FormControl(null, [Validators.required]),
    isGeneric: new FormControl('False', [Validators.required]),
    payingPrice: new FormControl(null)
  });
  public isSearching = false;
  public uploadForm: FormGroup = new FormGroup({
    csvFile: new FormControl('')
  });  
  public totalSaved = 0;
  

  constructor(private searchService: SearchService) { }

  ngOnInit(): void {
  }

  onFileSelect(event: any) {
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.uploadForm.get('csvFile')!.setValue(file);
    }
  }

  getTotalSavings() {
    let price_sum = 0
      for (let i = 0; i < this.searchResults.medications.length; i++) {
        if (this.searchResults.medications[i]['price_data']['save_amount'] > 0) {
          price_sum += this.searchResults.medications[i]['price_data']['save_amount']
        } 
      }
    this.totalSaved = price_sum;
  }

  searchTerm() {
    let searchVM: SearchVM = {
      name: this.searchForm.controls.name.value,
      form: this.searchForm.controls.medForm.value,
      dosage: this.searchForm.controls.dosage.value,
      dosageUnits: this.searchForm.controls.dosageUnits.value,
      zipCode: this.searchForm.controls.zipCode.value,
      quantity: this.searchForm.controls.quantity.value,
      isGeneric: this.searchForm.controls.isGeneric.value,
      buyerPrice: this.searchForm.controls.payingPrice.value
    }
    this.isSearching = true;
    this.searchService.searchTerm(searchVM).subscribe((data => {
      this.searchResults = data
      let price_sum = 0
      for (let i = 0; i < this.searchResults.medications.length; i++) {
        if (this.searchResults.medications[i]['price_data']['save_amount'] > 0) {
          price_sum += this.searchResults.medications[i]['price_data']['save_amount']
        } 
      }
      this.getTotalSavings();
      this.isSearching = false;
    }))
  }

  onCsvSubmit() {
    const formData = new FormData();
    this.isSearching = true;
    formData.append('file', this.uploadForm.get('csvFile')!.value);
    this.searchService.bulkSearch(formData).subscribe((data) => {
      this.searchResults = data;
      //console.log(data)
      this.getTotalSavings();
      this.isSearching = false;
    })
  }

}
