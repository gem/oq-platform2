#!/bin/bash
set -x
CA_PREFIX=gem_CA_
if [ "$1" = "-init" ]; then
    CA_SUFFIX="$2"
    CA_PATH="${CA_PREFIX}${CA_SUFFIX}"
    mkdir $CA_PATH
    mkdir $CA_PATH/private
    mkdir $CA_PATH/newcerts
    mkdir $CA_PATH/srccerts
    touch $CA_PATH/index.txt
    echo "01" > $CA_PATH/serial
    sed "s/#CA_SUFFIX#/$CA_SUFFIX/g" < openssl.cnf.tmpl > openssl_${CA_SUFFIX}.cnf
    openssl req -config ./openssl_${CA_SUFFIX}.cnf -new -x509 -keyout ${CA_PATH}/private/cakey.pem -out ${CA_PATH}/cacert.pem -days 3650
elif [ "$1" = "-stunnel" ]; then
    shift
    CA_SUFFIX="$1"
    CA_PATH="${CA_PREFIX}${CA_SUFFIX}"
    name="$2"
    openssl req -config ./openssl_${CA_SUFFIX}.cnf -new -keyout ${name}_newreq.pem -out ${name}_newreq.pem -days 3650
    openssl ca -config ./openssl_${CA_SUFFIX}.cnf -policy policy_anything -out ${name}_newcert.pem -infiles ${name}_newreq.pem
    openssl rsa -in ${name}_newreq.pem -out ${name}_newkey.pem
    sed -n '/-----BEGIN RSA PRIVATE KEY-----/,/-----END RSA PRIVATE KEY-----/p' ${name}_newkey.pem > ${name}.pem
    sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' ${name}_newcert.pem >> ${name}.pem
    mv ${name}_newreq.pem  ${CA_PATH}/srccerts
    mv ${name}_newkey.pem  ${CA_PATH}/srccerts
    mv ${name}_newcert.pem ${CA_PATH}/srccerts
    cp ${name}.pem ${CA_PATH}/srccerts
else
    CA_SUFFIX="$1"
    CA_PATH="${CA_PREFIX}${CA_SUFFIX}"
    echo "obase=16 ; $(date +%s)" | bc > $CA_PATH/serial
    name="$2"
    openssl req -config ./openssl_${CA_SUFFIX}.cnf -new -keyout ${name}_newreq.pem -extensions v3_req -out ${name}_newreq.pem -days 3650
    openssl ca -config ./openssl_${CA_SUFFIX}.cnf -days 3650 -policy policy_anything -extensions v3_req -out ${name}_newcert.pem -infiles ${name}_newreq.pem
    openssl rsa -in ${name}_newreq.pem -out ${name}_newkey.pem

    mv ${name}_newreq.pem  oq-platform.req
    mv ${name}_newkey.pem  oq-platform.key
    mv ${name}_newcert.pem oq-platform.crt
    cp ${CA_PATH}/cacert.pem oq-platform_CA.pem
fi

