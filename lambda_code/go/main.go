package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/aws/aws-lambda-go/lambda"
	"io/ioutil"
	"os"
	"sort"
	"strings"
	"time"
)

type Origin struct {
	Country string `json:"country"`
	Year    int    `json:"year"`
}

type Vehicle struct {
	Make         string
	Model        string
	LicensePlate string `json:"license_plate"`
	Origin       Origin
}

type VehicleWithHash struct {
	Make          string `json:"make"`
	Model         string `json:"model"`
	LicensePlate  string `json:"license_plate"`
	Origin        Origin `json:"origin"`
	MakeModelHash string `json:"make_model_hash"`
}

func HandleLambdaEvent() error {
	t1 := time.Now()

	// Load the file from JSON into memory
	file_name := os.Getenv("TEST_DATA_FILE")
	jsonFile, err := os.Open(fmt.Sprintf("/opt/%s", file_name))
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()

	byteValue, _ := ioutil.ReadAll(jsonFile)
	var sourceMap map[string]Vehicle
	json.Unmarshal([]byte(byteValue), &sourceMap)
	fmt.Printf("JSON parsing took %d ms\n", time.Now().Sub(t1).Milliseconds())

	t2 := time.Now()
	vector := []VehicleWithHash{}
	// For every item, check its license plate. If it has an 'A' in the first
	// section and a 0 in the second section, add it to the list. For example
	// 'AT-001-B' matches, but 'A-924-VW' doesn't.
	for _, vehicle := range sourceMap {
		comps := strings.Split(vehicle.LicensePlate, "-")
		if strings.Contains(comps[0], "A") && strings.Contains(comps[1], "0") {
			makeModelHash := sha256.Sum256([]byte(fmt.Sprintf(
				"%s%s", vehicle.Make, vehicle.Model,
			)))

			// Add it to the results list
			vector = append(
				vector,
				VehicleWithHash{
					Make:          vehicle.Make,
					Model:         vehicle.Model,
					LicensePlate:  vehicle.LicensePlate,
					Origin:        vehicle.Origin,
					MakeModelHash: strings.ToUpper(hex.EncodeToString(makeModelHash[:])),
				},
			)
		}
	}
	fmt.Printf("Object filtering took %d ms\n", time.Now().Sub(t2).Milliseconds())

	// Sort the list on license plate
	sort.Slice(vector, func(i, j int) bool {
		return vector[i].LicensePlate < vector[j].LicensePlate
	})

	// Convert it to a JSON string
	j, err := json.Marshal(vector)
	if err != nil {
		fmt.Println(err)
	}

	// Calculate the hash of that JSON string
	resultHash := sha256.Sum256([]byte(string(j)))
	resultHashStr := strings.ToUpper(hex.EncodeToString(resultHash[:]))

	duration := time.Now().Sub(t1)
	fmt.Printf(
		"Filtered %d from %d source items. Result hash: %s. Duration: %d ms.\n",
		len(vector), len(sourceMap), resultHashStr, duration.Milliseconds(),
	)

	return nil
}

func main() {
	lambda.Start(HandleLambdaEvent)
}
