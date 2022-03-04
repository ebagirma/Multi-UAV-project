import { Component, OnInit } from '@angular/core';

import {Map, Marker, Layer, Popup} from 'mapbox-gl';
import * as Draw from 'mapbox-gl-draw';
import { PerimeterService } from '../../services/perimeter.service';
import {ActivatedRoute} from '@angular/router';

let vm;

@Component({
  selector: 'app-maps',
  templateUrl: './maps.component.html',
  styleUrls: ['./maps.component.css']
})
export class MapsComponent implements OnInit {
  title = 'mapfrontend';
  map: Map;
  id = 0;
  marker: Marker = undefined;
  path = [];
  drones: any[] = [];
  pathMarkers = {};
  layer: Layer = undefined;
  draw: Draw;
  layers = {};
  save = 0;
  colors = ["black", "red", "green", "yellow"];
  
  constructor(private perimeter: PerimeterService, private activatedRoute: ActivatedRoute) {
    this.activatedRoute.params.subscribe((value) => {
      this.id = Number.parseInt(value.id, 10);
    });
  }

  ngOnInit() {
    this.getDrones();
    vm = this;
  }



  onDragEnd({target}) {
    const lngLat = target.getLngLat();
    // console.log(lngLat);
  }

  updateRoute({target}) {
    const lngLat = target.getLngLat();
    const marker = target.getElement().id;
    const [_, drone, index] = marker.split("-");
    const points = vm.path[drone];
    points[Number.parseInt(index)] = [lngLat.lng, lngLat.lat];


    vm.map.getSource(`route${drone}`).setData({
      'type': 'Feature',
      'properties': {},
      'geometry': {
        'type': 'LineString',
        'coordinates': points
      }
    });
    vm.save = Number.parseInt(drone);
    vm.path[drone] = points; 
  }

  updateSchedule() {
    this.perimeter.updateSchedule(this.path[this.save], this.save)
    .subscribe(({success}: any) => {
      console.log(success);
      this.save = 0;
    }, (err) => console.log(err));
  }


  load(event) {
    this.map = event;
    this.perimeter.getPerimeter(this.id).subscribe((perimeter: any) => this.updatePerimeter(perimeter),
      (err) => console.log(err));
    this.draw = new Draw({
      displayControlsDefault: false,
      controls: {
        polygon: true,
        trash: true
      }
    });
    this.map.addControl(this.draw);
    this.map.on('draw.create', ({features}) => {
      vm.perimeter.setPerimeter(features[0].geometry.coordinates, this.id).subscribe((perimeter: any) => this.updatePerimeter(perimeter),
        (error) => console.log(error));
    });
  }

  updatePerimeter(perimeter) {
    if (this.marker === undefined) {
      this.marker = new Marker({
        draggable: false,
        color: "green"
      });
    }
    this.map.setCenter([perimeter.home.lon, perimeter.home.lat]);
    this.marker.setLngLat([perimeter.home.lon, perimeter.home.lat])
      .setPopup(new mapboxgl.Popup({ offset: 25 }) // add popups
      .setHTML('<h5>Home Location</h5><div>This is your battery swapping station.</div>'))
      .addTo(this.map);
    this.marker.on('dragend', this.onDragEnd);
    const coordinates = [];
    perimeter.location_polygon.forEach(element => {
      // console.log(element);
      coordinates.push([element.lon, element.lat]);
    });
    if (this.layer !== undefined) {
      this.map.removeLayer('farm');
    }
    // } catch (e) {}
    if (this.layer === undefined) {
      this.layer = {
        id: 'farm',
        type: 'fill',
        source: {
          type: 'geojson',
          data: {
            type: 'Feature',
            geometry: {
              type: 'Polygon',
              coordinates: [coordinates]
            },
            properties: {}
          }
        },
        layout: {},
        paint: {
          'fill-color': '#007d88',
          'fill-opacity': 0.8
        }
      };
      this.map.addLayer(this.layer);
    } else {
      // this.map.removeLayer('farm');
      // this.layer.source.data.coordinates = coordinates;
      // console.log(coordinates);
      this.layer.source = {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [coordinates]
          },
          properties: {}
        }
      };
    }
  }

  updateArea({features}) {
    // this.draw = event;
    // console.log(features[0].geometry.coordinates);
    // console.log(this);
    this.perimeter.setPerimeter(features[0].geometry.coordinates, this.id).subscribe((perimeter: any) => this.updatePerimeter(perimeter),
      (error) => console.log(error));
  }

  surveySchedule() {
    this.perimeter.surveyPlan(this.id).subscribe(({success, path}: any) => {
      if (success) {
        this.path = path;
        console.log(this.path);
        this.drones.forEach((drone, iii) => {
          if (this.pathMarkers[drone.id]) {
            this.pathMarkers[drone.id].forEach(marker => {
              marker.remove();
            });
          }
          this.pathMarkers[drone.id] = [];
          path[drone.id].forEach((point, index) => {
            var el = document.createElement('div');
            /* Assign a unique `id` to the marker. */
            el.id = `marker-${drone.id}-${index}`;
            /* Assign the `marker` class to each marker for styling. */
            el.className = 'marker';
            const marker = new Marker({draggable: true, element: el});
            marker.on('dragend', this.updateRoute);
            marker.setLngLat(point).addTo(this.map);
            this.pathMarkers[drone.id].push(marker);
          });
          if (this.layers[drone.id]) {
            console.log("here");
            // this.map.removeLayer(`route${drone.id}`);
            this.map.getSource(`route${drone.id}`).setData({
                'type': 'Feature',
                'properties': {},
                'geometry': {
                  'type': 'LineString',
                  'coordinates': path[drone.id]
                }
              });
          } else {
              this.map.addSource(`route${drone.id}`, {
              'type': 'geojson',
              'data': {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                  'type': 'LineString',
                  'coordinates': path[drone.id]
                }
              }
            });
            this.map.addLayer({
              'id': `route${drone.id}`,
              'type': 'line',
              'source': `route${drone.id}`,
              'layout': {
                'line-join': 'round',
                'line-cap': 'round'
              },
              'paint': {
                'line-color': this.colors[iii % this.colors.length],
                'line-width': 3
              }
            });
          }
          this.layers[drone.id] = 1;
        });
      }
    }, (error) => console.log(error));
    this.save = 0;
  }

  scanDrones() {
    this.perimeter.scanDrones(this.id).subscribe(({success, drones}: any) => {
      if (success) {
        // console.log(this.drones);
        this.drones = drones;
      }
    }, (error) => console.log(error));
  }

  getDrones() {
    this.perimeter.getDrones(this.id).subscribe((drones: any[]) => {
        // console.log(this.drones);
        this.drones = drones;
    }, (error) => console.log(error));
  }

}
