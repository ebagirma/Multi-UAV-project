import { Component, OnInit } from '@angular/core';
import {PerimeterService} from '../../../services/perimeter.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-create-farm',
  templateUrl: './create-farm.component.html',
  styleUrls: ['./create-farm.component.css']
})
export class CreateFarmComponent implements OnInit {
  name;
  description;
  city;
  constructor(private perimeterService: PerimeterService, private route: Router) { }

  ngOnInit() {
  }

  createFarm($event: MouseEvent) {
    $event.preventDefault();
    this.perimeterService.createFarm({name: this.name, description: this.description, city: this.city})
      .subscribe(() => {
        this.route.navigate(['/farms']);
      }, (e) => console.log(e));
  }
}
