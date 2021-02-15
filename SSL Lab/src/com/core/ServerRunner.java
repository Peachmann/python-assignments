package com.core;

import com.core.servers.OwnSslServer;
import com.core.servers.SslServer;

import java.io.IOException;

public class ServerRunner {

    public static void main(String[] args) throws IOException {

        /* 2. */
        //new SslServer();

        /* 6. */
        new OwnSslServer();
    }
}
