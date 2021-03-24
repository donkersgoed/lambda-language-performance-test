#[macro_use]
extern crate lambda_runtime as lambda;
#[macro_use]
extern crate serde_derive;
extern crate simple_logger;

use lambda::error::HandlerError;
use sha2::{Sha256, Digest};

use std::env;
use std::collections::HashMap;
use std::error::Error;
use std::fs;
use std::time::Instant;

#[derive(Serialize, Deserialize, Clone)]
struct Origin {
    country: String,
    year: u16
}

#[derive(Deserialize)]
struct Vehicle {
    make: String,
    model: String,
    license_plate: String,
    origin: Origin
}

#[derive(Serialize)]
struct VehicleWithHash {
    make: String,
    model: String,
    license_plate: String,
    origin: Origin,
    make_model_hash: String
}

#[derive(Deserialize, Clone)]
struct CustomEvent {}

#[derive(Serialize, Clone)]
struct CustomOutput {
    message: String,
}

fn main() -> Result<(), Box<dyn Error>> {
    lambda!(my_handler);

    Ok(())
}

fn my_handler(_: CustomEvent, _: lambda::Context) -> Result<(), HandlerError> {
    let start = Instant::now();

    // Load the file from JSON into memory
    let file_name = env::var("TEST_DATA_FILE").unwrap();
    let data = fs::read_to_string(
        format!("/opt/{}", file_name)
    ).expect("Unable to read file");
    let map: HashMap<String, Vehicle> = serde_json::from_str(&data).unwrap();

    let mut vec = Vec::<VehicleWithHash>::new();
    // For every item, check its license plate. If it has an 'A' in the first
    // section and a 0 in the second section, add it to the list. For example
    // 'AT-001-B' matches, but 'A-924-VW' doesn't.
    for (_, v) in &map {
        let comps: Vec<&str> = v.license_plate.split('-').collect();
        if comps[0].contains("A") && comps[1].contains("0") {
            let mut hasher = Sha256::new();
            hasher.update(format!("{}{}", v.make, v.model));

            // Add it to the results list
            vec.push(
                VehicleWithHash {
                    make_model_hash: format!("{:X}", hasher.finalize()),
                    make: v.make.clone(),
                    model: v.model.clone(),
                    origin: v.origin.clone(),
                    license_plate: v.license_plate.clone()
                }
            );
        }
    }
    
    // Sort the list on license plate
    vec.sort_by_key(|k| k.license_plate.clone());

    // Convert it to a JSON string
    let json_out = serde_json::to_string(&vec).unwrap();

    // Calculate the hash of that JSON string
    let mut hasher = Sha256::new();
    hasher.update(json_out);
    let result_hash = format!("{:X}", hasher.finalize());

    let duration = start.elapsed().as_millis();
    println!(
        "Filtered {} from {} source items. Result hash: {}. Duration: {:?} ms.", 
        vec.len(), map.keys().len(), result_hash, duration
    );

    Ok(())
}
