package com.example.mimirdemo

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController


@Composable
fun MainMenuScreen(navController: NavHostController) {
    // State variables for username and password fields
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    // Box with a gray background
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF9b9ca5)),
        contentAlignment = Alignment.Center
    ) {
        // Column to layout the components vertically
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Logo (replace with your actual image in the drawable folder)
            Image(
                painter = painterResource(id = R.drawable.mimir_scaled), // Placeholder logo
                contentDescription = "App Logo",
                modifier = Modifier.size(300.dp) // Adjust size as necessary
            )

            Text(
                text = "Mimir", // Your custom text here
                color = Color(0xFF202e46), // Set the custom color (white)
                fontSize = 60.sp, // Set the font size
                fontFamily = FontFamily(Font(R.font.pac)),
                //fontWeight = FontWeight.Bold, // Set the font weight
                textAlign = TextAlign.Center, // Align text in the center
                //modifier = Modifier.padding(top = 8.dp) // Add padding above the text
            )
            Spacer(modifier = Modifier.height(16.dp)) // Space between logo and TextFields

            // Username TextField
            OutlinedTextField(
                value = username,
                onValueChange = { username = it },
                label = { Text("Username") },
                modifier = Modifier.fillMaxWidth(),
            )


            Spacer(modifier = Modifier.height(24.dp)) // Space before the button

            // Enter Button
            Button(
                onClick = { navController.navigate("modeScreen") },
                modifier = Modifier
                        .width(150.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF8c8d95), // Background color
                    contentColor = Color.White // Text color
                )
            ) {


                Text("Enter")
            }
        }
    }
}