package com.core.servers;

import com.sun.net.httpserver.*;

import javax.net.ssl.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.util.List;

public class OwnSslServer {
    public static class MyHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            List<String> lines = Files.readAllLines(Paths.get("html_response.txt"), StandardCharsets.US_ASCII);
            StringBuilder response = new StringBuilder();
            for(String i : lines) {
                response.append(i).append("\n");
            }
            byte[] resp = response.toString().getBytes();

            t.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
            t.sendResponseHeaders(200, resp.length);

            OutputStream os = t.getResponseBody();
            os.write(resp);
            os.close();

            System.out.println("Response sent!");
        }
    }

    public OwnSslServer() {
        try {
            // setup the socket address
            InetSocketAddress address = new InetSocketAddress(443);

            // initialise the HTTPS server
            HttpsServer httpsServer = HttpsServer.create(address, 0);
            SSLContext sslContext = SSLContext.getInstance("SSL");

            // initialise the keystore
            char[] kspassword = "root".toCharArray();
            KeyStore ks = KeyStore.getInstance("JKS");
            FileInputStream fis = new FileInputStream("server-store.pfx");
            ks.load(fis, kspassword);

            // setup the key manager factory
            KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
            kmf.init(ks, kspassword);

            char[] tspassword = "storepassword".toCharArray();
            KeyStore ts = KeyStore.getInstance("JKS");
            FileInputStream tsreader = new FileInputStream("server-truststore.jks");
            ts.load(tsreader, tspassword);

            // setup the trust manager factory
            TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
            tmf.init(ts);

            // setup the HTTPS context and parameters
            sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);
            httpsServer.setHttpsConfigurator(new HttpsConfigurator(sslContext) {
                public void configure(HttpsParameters params) {
                    try {
                        // initialise the SSL context
                        SSLContext context = getSSLContext();
                        SSLEngine engine = context.createSSLEngine();
                        params.setNeedClientAuth(false);
                        params.setCipherSuites(engine.getEnabledCipherSuites());
                        params.setProtocols(engine.getEnabledProtocols());

                        // Set the SSL parameters
                        SSLParameters sslParameters = context.getSupportedSSLParameters();
                        params.setSSLParameters(sslParameters);

                    } catch (Exception ex) {
                        System.out.println("Failed to create HTTPS port.");
                    }
                }
            });

            httpsServer.createContext("/index", new MyHandler());
            httpsServer.setExecutor(null);
            httpsServer.start();

            System.out.println("Waiting for requests.");

        } catch (Exception exception) {
            System.out.println("Failed to create HTTPS server.");
            exception.printStackTrace();
        }
    }
}
