package com.core.clients;

import javax.net.ssl.*;
import java.io.*;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

public class OwnSslClient {
    public OwnSslClient() {
        try {
            KeyStore ks = KeyStore.getInstance("JKS");
            ks.load(new FileInputStream("client.pfx"), "root".toCharArray());

            KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
            kmf.init(ks, "root".toCharArray());

            char[] tspassword = "storepassword".toCharArray();
            KeyStore ts = KeyStore.getInstance("JKS");
            FileInputStream tsreader = new FileInputStream("client-truststore.jks");
            ts.load(tsreader, tspassword);

            // setup the trust manager factory
            TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
            tmf.init(ts);

            SSLContext sc = SSLContext.getInstance("TLS");
            sc.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);

            SSLSocketFactory factory =
                    sc.getSocketFactory();
            SSLSocket socket =
                    (SSLSocket)factory.createSocket("www.bnr.ro", 443);

            socket.startHandshake();

            SSLSession session = socket.getSession();
            Certificate peerCertificate = session.getPeerCertificates()[0];

            CertificateFactory cf = CertificateFactory.getInstance("X.509");
            ByteArrayInputStream bais = new ByteArrayInputStream(peerCertificate.getEncoded());
            X509Certificate x509 =  (X509Certificate) cf.generateCertificate(bais);

            System.out.println("Version: " + x509.getVersion());
            System.out.println("Serial number: " + x509.getSerialNumber());
            System.out.println("Issued by: " + x509.getIssuerDN());
            System.out.println("Issued at: " + x509.getNotBefore());
            System.out.println("Expires at: " + x509.getNotAfter());

            System.out.println("Subject name: " + x509.getSubjectDN());
            System.out.println("Subject alternative names: " + x509.getSubjectAlternativeNames());

            System.out.println("Encryption algorithm: " + x509.getSigAlgName());
            System.out.println("Public key: " + peerCertificate.getPublicKey());

            PrintWriter out = new PrintWriter(
                    new BufferedWriter(
                            new OutputStreamWriter(socket.getOutputStream())));

            // send GET request
            out.println("GET / HTTP/1.0");
            out.println();
            out.flush();

            // read response
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(
                            socket.getInputStream()));

            FileWriter outFile = new FileWriter("out_1.txt");
            String inputLine;
            while ((inputLine = in.readLine()) != null)
                outFile.write(inputLine + "\n");

            in.close();
            out.close();
            socket.close();
            outFile.close();

        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Invalid certificate! Possibly self-signed or not from a trusted issuer.");
        }
    }
}
