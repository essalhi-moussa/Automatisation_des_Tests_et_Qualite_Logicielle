package ma.fsac.qa.utils;

import org.testng.IRetryAnalyzer;
import org.testng.ITestResult;

/** Relance un test au maximum deux fois. Reserve aux tests qui dependent d un site externe instable. */
public class RetryAnalyzer implements IRetryAnalyzer {

    private static final int MAX_RETRY = 2;
    private int count = 0;

    @Override
    public boolean retry(ITestResult result) {
        return count++ < MAX_RETRY;
    }
}
