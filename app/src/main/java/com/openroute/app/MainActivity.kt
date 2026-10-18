package com.openroute.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.InetAddress
import java.net.URL

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    OpenRouteScreen()
                }
            }
        }
    }
}

data class TestResult(
    val target: String,
    val dnsOk: Boolean,
    val httpCode: Int?,
    val latency: Long?,
    val error: String?
)

@Composable
fun OpenRouteScreen() {
    var results by remember { mutableStateOf<List<TestResult>>(emptyList()) }
    var isTesting by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "🌐 OpenRoute v0.2.0",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        Button(
            onClick = {
                isTesting = true
                scope.launch {
                    results = runTests()
                    isTesting = false
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            enabled = !isTesting
        ) {
            Text(if (isTesting) "Test ediliyor..." else "🔍 Bağlantı Testi Başlat")
        }

        if (isTesting) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
        }

        Spacer(modifier = Modifier.height(16.dp))

        results.forEach { result ->
            TestResultCard(result)
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
fun TestResultCard(result: TestResult) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (result.dnsOk && (result.httpCode == 200 || result.httpCode == 404))
                MaterialTheme.colorScheme.primaryContainer
            else MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = result.target,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text("DNS: ${if (result.dnsOk) "✅ Çözüldü" else "❌ Başarısız"}")
            result.httpCode?.let { Text("HTTP Kodu: $it") }
            result.latency?.let { Text("Gecikme: ${it}ms") }
            result.error?.let { 
                Text(
                    "Hata: $it",
                    color = MaterialTheme.colorScheme.error
                ) 
            }
        }
    }
}

suspend fun runTests(): List<TestResult> = withContext(Dispatchers.IO) {
    val targets = listOf(
        "instagram.com",
        "tiktok.com",
        "github.com",
        "google.com"
    )
    
    targets.map { target ->
        testTarget(target)
    }
}

fun testTarget(target: String): TestResult {
    var dnsOk = false
    var httpCode: Int? = null
    var latency: Long? = null
    var error: String? = null
    
    try {
        val startTime = System.currentTimeMillis()
        InetAddress.getByName(target)
        dnsOk = true
        latency = System.currentTimeMillis() - startTime
    } catch (e: Exception) {
        error = "DNS hatası: ${e.message}"
        return TestResult(target, dnsOk, httpCode, latency, error)
    }
    
    try {
        val url = URL("https://$target")
        val connection = url.openConnection() as HttpURLConnection
        connection.connectTimeout = 10000
        connection.readTimeout = 10000
        connection.requestMethod = "GET"
        connection.connect()
        httpCode = connection.responseCode
        connection.disconnect()
    } catch (e: Exception) {
        error = "HTTPS hatası: ${e.message}"
    }
    
    return TestResult(target, dnsOk, httpCode, latency, error)
}
