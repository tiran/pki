//
// Copyright Red Hat, Inc.
//
// SPDX-License-Identifier: GPL-2.0-or-later
//
package org.dogtagpki.acme.server;

import java.util.Collection;
import java.util.Date;

import org.dogtagpki.acme.ACMEAccount;
import org.dogtagpki.acme.ACMEAuthorization;
import org.dogtagpki.acme.ACMEChallenge;
import org.dogtagpki.acme.ACMEOrder;
import org.dogtagpki.acme.validator.ACMEValidator;

/**
 * @author Endi S. Dewata
 */
public class ACMEChallengeProcessor implements Runnable {

    public static org.slf4j.Logger logger = org.slf4j.LoggerFactory.getLogger(ACMEChallengeProcessor.class);

    ACMEAccount account;
    ACMEAuthorization authorization;
    ACMEChallenge challenge;
    ACMEValidator validator;

    public ACMEChallengeProcessor(
            ACMEAccount account,
            ACMEAuthorization authorization,
            ACMEChallenge challenge,
            ACMEValidator validator) {

        this.account = account;
        this.authorization = authorization;
        this.challenge = challenge;
        this.validator = validator;
    }

    public void run() {
        try {
            processChallenge();
        } catch (Exception e) {
            logger.error("Unable to process challenge " + challenge.getID() + ": " + e.getMessage(), e);
        }
    }

    public void processChallenge() throws Exception {

        String challengeID = challenge.getID();
        logger.info("Processing challenge " + challengeID);

        try {
            validator.validateChallenge(authorization, challenge);
            finalizeValidAuthorization();

        } catch (Exception e) {
            finalizeInvalidAuthorization(e);
        }
    }

    public void finalizeValidAuthorization() throws Exception {

        ACMEEngine engine = ACMEEngine.getInstance();
        String authzID = authorization.getID();
        String challengeID = challenge.getID();

        logger.info("Challenge " + challengeID + " is valid");
        challenge.setStatus("valid");
        challenge.setValidationTime(new Date());

        logger.info("Authorization " + authzID + " is valid");
        authorization.setStatus("valid");

        engine.updateAuthorization(account, authorization);

        logger.info("Updating pending orders");

        Collection<ACMEOrder> orders =
            engine.getOrdersByAuthorizationAndStatus(account, authzID, "pending");

        for (ACMEOrder order : orders) {
            boolean allAuthorizationsValid = true;

            for (String orderAuthzID : order.getAuthzIDs()) {

                ACMEAuthorization authz = engine.getAuthorization(account, orderAuthzID);
                if (authz.getStatus().equals("valid")) continue;

                allAuthorizationsValid = false;
                break;
            }

            if (!allAuthorizationsValid) continue;

            logger.info("Order " + order.getID() + " is ready");
            order.setStatus("ready");

            engine.updateOrder(account, order);
        }
    }

    public void finalizeInvalidAuthorization(Exception e) throws Exception {

        ACMEEngine engine = ACMEEngine.getInstance();
        String authzID = authorization.getID();
        String challengeID = challenge.getID();

        // RFC 8555 Section 8.2: Retrying Challenges
        //
        // The server MUST provide information about its retry state to the
        // client via the "error" field in the challenge and the Retry-After
        // HTTP header field in response to requests to the challenge resource.
        // The server MUST add an entry to the "error" field in the challenge
        // after each failed validation query.  The server SHOULD set the Retry-
        // After header field to a time after the server's next validation
        // query, since the status of the challenge will not change until that
        // time.

        logger.info("Challenge " + challengeID + " is invalid");
        challenge.setStatus("invalid");

        engine.updateAuthorization(account, authorization);
    }
}
