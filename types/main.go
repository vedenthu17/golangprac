package main

import "fmt"

func main() {

	var username string = "name"

	fmt.Println(username)
	fmt.Printf("Variable is of type %T \n", username)

	var isloggedin bool = true

	fmt.Println(isloggedin)
	fmt.Printf("Variable is of type %T \n", username)

	var smallvalue uint = 257

	fmt.Println(smallvalue)
	fmt.Printf("Variable is of type %T \n", smallvalue)
}
