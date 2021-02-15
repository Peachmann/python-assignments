package com.core;

import com.core.clients.OwnSslClient;
import com.core.clients.SslClient;

import java.io.IOException;

public class ClientRunner {
    public static void main(String[] args) throws IOException {
        /* 1. Simple request client */
        //new SslClient();

        /* 6. */
        new OwnSslClient();
    }
}
