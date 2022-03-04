import { Component, OnInit } from '@angular/core';
import {PerimeterService} from '../../services/perimeter.service';

@Component({
  selector: 'app-farms',
  templateUrl: './farms.component.html',
  styleUrls: ['./farms.component.css']
})
export class FarmsComponent implements OnInit {
  farms = [];
  constructor(private perimeterService: PerimeterService) { }

  ngOnInit() {
    this.perimeterService.getFarms().subscribe((farms: Array<any>) => {
      this.farms = farms;
      console.log(farms);
    }, (error) => {
      console.log(error);
    });
  }

}
