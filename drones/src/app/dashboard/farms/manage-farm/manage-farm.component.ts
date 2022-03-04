import { Component, OnInit } from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {PerimeterService} from '../../../services/perimeter.service';

@Component({
  selector: 'app-manage-farm',
  templateUrl: './manage-farm.component.html',
  styleUrls: ['./manage-farm.component.css']
})
export class ManageFarmComponent implements OnInit {
  id = '0';
  farm = {
    name: '',
    description: '',
    city: '',
    id: 0,
  };
  crops = [];
  plants = {};
  constructor(private route: ActivatedRoute, private perimeterService: PerimeterService) {
    this.route.params.subscribe((value) => {
      this.id = value.id;
    });
  }

  ngOnInit() {
    this.perimeterService.getFarmDetail(this.id).subscribe((farm: any) => {
      this.farm = farm.farm;
      this.crops = farm.crops;
      this.plants = farm.plants;
    }, error => console.log(error));
  }

}
