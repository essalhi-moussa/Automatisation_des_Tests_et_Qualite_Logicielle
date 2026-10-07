package ma.fsac.qa.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Acces centralise a la configuration.
 * Priorite : propriete systeme (-Dx=y) > variable d'environnement > config.properties.
 */
public final class Config {

    private static final Properties PROPS = new Properties();

    static {
        try (InputStream in = Config.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (in == null) {
                throw new IllegalStateException("config.properties introuvable dans le classpath");
            }
            PROPS.load(in);
        } catch (IOException e) {
            throw new IllegalStateException("Lecture de config.properties impossible", e);
        }
    }

    private Config() {
    }

    public static String get(String key) {
        String sys = System.getProperty(key);
        if (sys != null && !sys.isBlank() && !sys.startsWith("${")) {
            return sys;
        }
        String env = System.getenv(key.toUpperCase().replace('.', '_'));
        if (env != null && !env.isBlank()) {
            return env;
        }
        return PROPS.getProperty(key);
    }

    public static int getInt(String key) {
        return Integer.parseInt(get(key).trim());
    }

    public static boolean getBoolean(String key) {
        return Boolean.parseBoolean(get(key).trim());
    }

    public static String uiBaseUrl() {
        return get("ui.base.url");
    }

    public static String iframeBaseUrl() {
        return get("iframe.base.url");
    }

    public static String apiBaseUrl() {
        return get("api.base.url");
    }

    /** Cle API Reqres : variable d'environnement REQRES_API_KEY, sinon config.properties. */
    public static String apiKey() {
        String env = System.getenv("REQRES_API_KEY");
        return (env != null && !env.isBlank()) ? env : get("api.key");
    }
}
