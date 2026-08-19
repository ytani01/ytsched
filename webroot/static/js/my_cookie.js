/**
 *
 */
class MyCookie {
    constructor() {
        this.cookie = undefined;
        this.data = {};
        this.load();
    }

    /**
     * @return {Object} data
     */
    load() {
        const allcookie = document.cookie;
        // console.log(`MyCookie.load>allcookie="${allcookie}"`);

        if ( allcookie.length == 0 ) {
            return {};
        }

        for (let ent of allcookie.split("; ")) {
            let [k, v] = ent.split('=');
            // console.log(`MyCookie.load>k=${k},v=${v}`);
            this.data[k] = v;
        } // for(i)

        return this.data;
    } // MyCookie.load()

    /**
     * 
     */
    save() {
        if ( Object.keys(this.data) ) {
            return;
        }

        let allcookie = "";
        for (let key in this.data) {
            allcookie += `${key}=${this.data[key]};`;
        } // for (key)

        document.cookie = allcookie;
    }

    /**
     * @param {string} key
     * @param {string} value
     */
    set(key, value) {
        document.cookie = `${key}=${encodeURIComponent(value)};`;
    }
    
    /**
     * @param {string} key
     */
    get(key) {
        if ( this.data[key] === undefined ) {
            return undefined;
        }
        return decodeURIComponent(this.data[key]);
    } // MyCookie.get()
} // class MyCookie
