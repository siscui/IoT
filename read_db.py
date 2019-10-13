from firestore_manager import FirestoreManager


def handler(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(u'Received document snapshot: {}'.format(doc.id))
        doc_dict = doc.to_dict()
        print(doc_dict['bombaAgua']['activo'])
        doc_dict['bombaAgua']['activo'] = False
        fsm.set(doc_dict)


cred = {
    "type": "service_account",
    "project_id": "siscui",
    "private_key_id": "981046b404eeffb01b35caacd90b78f07557a662",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDRK48Zidjp+/oO\nq7a54x0RnWmXlaCrYHkslsCg6A9lsFVebr+4KLy8nb6hw+pqgx9ur0s1LmZYH0qR\nkIIH0FZh7UmJA0AKENtg3e3LYassFlReHCH2wfcQ+yOIHJmg3At1MI9EdIqc8RPY\npKCGRctjMnBnszpN+UfqB79mg/07Efn6mi45mZzv7kBrjKgcN6uKmiyVcUW7BVWb\n0KNM0org5KqGfAPNqUFQBw/7S1iJTf37TJ8/KoRwOCKZtf96+TWEQb9ZymTG0jAi\nTdtYzj5Ad0FnZ2rKXb3AlnGSF2lJIX023BxyW5ova7jte13XnBgfXYfwUf4T9jrQ\nqKly1eUPAgMBAAECggEAVnvVIfEN38jQXip/VaJizXqxQvyZvuIXl+kI4j6wxxG+\naloOKP2m87GhNU9E6B8o6uHNjcKOjFb7xO3j5YktfjXXFrBiVQcdPZLlFBdg58yf\nu32USWtvVPURfuCcYJc6oYyfX+VzvmorE4MV4A6RhoU/VpETRVQReOEVMTTXigko\nQEN+MSd66p3Do1/i4bcLvNvsiV31sbdcx++NqdvSSZ9vGyIUJ0X5IvvEyKV7kBlI\nymlzaCDKRQ0JGWMOfAkAAhfDCU3gFMF+HcfMo1CMssH8mDc8V8s4Fq6SY8ivZuss\nqMugnymShpSDvvBlw6rDByxCKAXyPuHE7d+c7RmAGQKBgQDv86qIIjkhgZVYqbh5\nDss2ylT3XaezbjYITDM0XF0kVLjFg3dQsQWRCENnFn1LAcsxlaGXPN8tYMKoJ9Sp\nWMflbFijjKBw15f1Wj+wGqwTJiSu0HI//7NeWaH8cuPWINw0u9KXLgwlOKQG8Zt+\nk8HNH9rxpa3OdDynFyqN+8qcmwKBgQDfKN1aoxvuHSOlqSzdjWG/anYm37GfE4Ae\nEgrNR04lCLr/wJ6KawFsV+4QABPSKjo0XsTkExI+rYNr5EKXNRVIFygt3U+A0dcW\nnRuNWEq8aZv6B2T7o4J1Ohd9AdjlRQYEVfZbZbcNV4gtJa2y9JoNdRnWzmB7f63A\nIaMdfVAunQKBgDL1TnwGuJdTC8J+mLys1Z9XLOAztY+3kiYE+MLf8q/qhir8FnS+\ng24fkSDtd8JcKSjonB6gQM1ERVKs0s78GcexUMm67b/JKW5jsi7WG0Ed0qCFiB3r\nUc5xvqL8S0KIS/uu/7Q3hUDKXJtU6C7jdj73yumSw+yaZt8dXl404PyNAoGAJUWs\nAvFvPsv7IjYpWi+8/b2IUmHWRt147ozQ5Qxdzu2wXfsL/85zhGcDSgTZSqbm5cxW\nUkmlKHbOlnyfaqXhEhNcEJ0AJGHn7Mz8xxTSFroE5TPK+ASNS4sSVTyzv0dSA/Nf\nnFBWzJGsGu5KHrOf71N5p1j84GOo34g+uDQv6jkCgYEA3xBUwYFbDyGEbukkeAJ1\nRcsNfqLhBMVOh7wz3b1ZECvMCjfCNmalVaN5AIgxM/Y2ImjYYi+X+El2p0QDJT6B\naNmy/qLuADn0uXEQjd0yyEd3M3d0tX6d7XtcIQ1DzZFWmoueWSdF7bl8nz4ANCn3\nPhk8AGu5AJ9njwoLa2gUFIA=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-qzw3h@siscui.iam.gserviceaccount.com",
    "client_id": "100595906723626256215",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-qzw3h%40siscui.iam.gserviceaccount.com"
}
doc_id = u'9gOhABtBYIToU5N4RRxV'

fsm = FirestoreManager(cred, doc_id)

fsm.on_snapshot(handler)

input()
