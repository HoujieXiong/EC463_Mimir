package com.example.mimirdemo

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController

@Composable
fun RecipeScreen(navController: NavHostController) {
    var recipeUrl by remember { mutableStateOf("") } // Stores the entered URL

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Enter Recipe URL",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Input field for recipe URL
        OutlinedTextField(
            value = recipeUrl,
            onValueChange = { recipeUrl = it },
            label = { Text("Recipe URL") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Submit Button (Functionality will be added later)
        Button(
            onClick = { /* TODO: Send URL to server */ },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Submit Recipe")
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Read Ingredients Button
        Button(
            onClick = { /* TODO: Request Ingredients from server */ },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Read Ingredients")
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Read Steps Button
        Button(
            onClick = { /* TODO: Request Steps from server */ },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Read Steps")
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Back Button
        Button(
            onClick = { navController.navigate("mainMenu") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Back to Menu")
        }
    }
}
