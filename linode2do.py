from linode.api import Api
import requests

class APIError(Exception):
    pass

class DigitalOceanEndpoint(object):
    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key

    def credentials(self, params={}):
        params.update({
            "client_id": self.client_id,
            "api_key": self.api_key,
        })
        return params

    def assert_ok(self, response):
        if response['status'] != 'OK':
            raise APIError(
                "API Error: {}".format(
                    response.get(
                        'error_message',
                        response.get(
                            'message',
                            "Unknown error ({})".format(response),
                        )
                    )
                )
            )


class Domains(list):
    class Domain(dict):
        class Records(list):
            class Record(dict):
                def __init__(self, domain, data=None):
                    self.domain = domain
                    self.update(data)

                def edit(self, record_type, data, **kwargs):
                    url = "https://api.digitalocean.com/domains/{}/records/{}".format(
                        self.domain['id'],
                        self['id'],
                    )

                    params = self.domain.api.credentials({
                        "record_type": record_type,
                        "data": data,
                    })
                    for param in kwargs:
                        if param not in ("name", "priority", "port", "weight"):
                            raise Exception("Unknown parameter {}".format(param))
                        params[param] = kwargs[param]

                    r = requests.get(url, data=params).json()
                    self.domain.api.assert_ok(r)
                    self.update(r['record'])
                    return self

                def destroy(self):
                    url = "https://api.digitalocean.com/domains/{}/records/{}/destroy".format(
                        self.domain['id'],
                        self['id'],
                    )
                    r = requests.get(url, data=self.domain.credentials())
                    self.domain.assert_ok(r)
                    return r

            def __init__(self, domain):
                self.domain = domain
                if 'id' in domain:
                    url = "https://api.digitalocean.com/domains/{}/records".format(
                        domain['id']
                    )
                    r = requests.get(url, data=domain.api.credentials()).json()
                    domain.api.assert_ok(r)
                    self.extend(r['records'])

            def new(self, record_type, data, **kwargs):
                url = "https://api.digitalocean.com/domains/{}/records/new".format(self.domain['id'])
                params = self.domain.api.credentials({
                    "record_type": record_type,
                    "data": data,
                })
                for param in kwargs:
                    if param not in ("name", "priority", "port", "weight"):
                        raise Exception("Unknown parameter {}".format(param))
                    params[param] = kwargs[param]

                r = requests.get(url, data=params).json()
                self.domain.api.assert_ok(r)
                return(r['record'])

            def __call__(self, record_id):
                url = 'https://api.digitalocean.com/domains/{}/records/{}'.format(
                    self.domain['id'],
                    record_id,
                )
                r = requests.get(url, data=self.domain.credentials()).json()
                self.domain.assert_ok(r)
                return self.Record(self.domain, r['record'])

        def __init__(self, api, domain_id):
            self.api = api
            url = "https://api.digitalocean.com/domains/{}".format(domain_id)
            r = requests.get(url, data=api.credentials()).json()
            api.assert_ok(r)
            self.update(r['domain'])
            self.records = self.Records(self)

        def credentials(self, params):
            return self.api.credentials(params)

        def assert_ok(self, response):
            return self.api.assert_ok(response)

        def destroy(self):
            url = "https://api.digitalocean.com/domains/{}/destroy".format(
                self['id']
            )
            r = requests.get(url, data=self.api.credentials()).json()
            self.api.assert_ok(r)
            return r

        def __repr__(self):
            return "<DigitalOceanDomain {}>".format(self['name'])

    def __init__(self, api):
        self.api = api
        url = 'https://api.digitalocean.com/domains'
        domain_list = requests.get(url, data=api.credentials()).json()
        api.assert_ok(domain_list)
        self[:] = [self.Domain(self.api, d['id']) for d in domain_list['domains']]

    def __call__(self, domain_id):
        return self.Domain(self.api, domain_id)

    def new(self, name, ip_address):
        url = "https://api.digitalocean.com/domains/new"
        r = requests.get(url, data=self.api.credentials(
            {"name": name, "ip_address": ip_address}
        )).json()
        self.api.assert_ok(r)
        domain = self.Domain(self.api, r['domain']['id'])
        self.append(domain)
        return domain


class Client(DigitalOceanEndpoint):
    def __init__(self, client_id, api_key):
        super(Client, self).__init__(client_id, api_key)

    def __getattr__(self, name):
        if name == 'domains': return Domains(self)
        raise AttributeError("Attribute not found: {}".format(name))


if __name__ == "__main__":
    ln = Api(raw_input("Enter your Linode API key: "))
    do = Client(
        client_id=raw_input("Enter your DigitalOcean client ID: "),
        api_key=raw_input("Enter your DigitalOcean API key: "),
    )

    for domain in ln.domain_list():
        domain_name = domain['DOMAIN']
        domain_id = domain['DOMAINID']
        records = ln.domain_resource_list(domainID=domain['DOMAINID'])
        www = [record for record in records if (
                    (record['NAME'] == 'www' and record['TYPE'].upper() == 'A') or
                    (record['NAME'] == '' and record['TYPE'].upper() == 'A')
              )]

        if not www:
            print "\tPulando", domain_name

        print "\tTransfering", domain_name
        ip = www[0]['TARGET']

        try:
            do_domain = do.domains(domain['DOMAIN'])
        except APIError:
            do_domain = do.domains.new(domain_name, ip)

        for record in records:
            record_type = record['TYPE'].upper()
            if record_type in ('NS', 'SOA'):
                continue
            print "\t\tRecord: {} {}".format(record_type, record['TARGET'])
            if record_type in ('MX', 'CNAME'):
                if "." in record['TARGET']:
                    if record['TARGET'][-1] != '.':
                        record['TARGET'] += '.'
                else:
                    record['TARGET'] += '.' + domain_name + '.'

            if not record['NAME']:
                record['NAME'] = '@'

            do_domain.records.new(
                record_type=record_type,
                data=record['TARGET'],
                name=record['NAME'],
                priority=record['PRIORITY'],
                port=record['PORT'],
                weight=record['WEIGHT'],
            )
